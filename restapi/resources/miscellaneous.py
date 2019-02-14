# -*- coding: utf-8 -*-

from restapi.rest.definition import EndpointResource
from restapi.services.detect import detector
from utilities.logs import get_logger

log = get_logger(__name__)


class Admin(EndpointResource):
    """ Token and Role authentication test """

    def get(self):
        return "I am admin!"


###########################
# In case you have celery queue,
# you get a queue endpoint for free
if detector.check_availability('celery'):

    class Queue(EndpointResource):

        def get(self, task_id=None):

            data = []
            # Inspect all worker nodes
            celery = self.get_service_instance('celery')

            if task_id is not None:
                task_result = celery.AsyncResult(task_id)
                res = task_result.result
                if not isinstance(res, dict):
                    res = str(res)
                return {
                    'status': task_result.status,
                    # 'info': task_result.info,
                    'output': res,
                }

            #############################
            # FAST WAY
            stats = celery.control.inspect().stats()
            workers = list(stats.keys())

            active_tasks = {}
            revoked_tasks = {}
            scheduled_tasks = {}
            reserved_tasks = {}

            for worker in workers:
                i = celery.control.inspect([worker])
                log.debug('checked worker: %s', worker)
                for key, value in i.active().items():
                    active_tasks[key] = value
                for key, value in i.revoked().items():
                    revoked_tasks[key] = value
                for key, value in i.reserved().items():
                    reserved_tasks[key] = value
                for key, value in i.scheduled().items():
                    scheduled_tasks[key] = value

            #############################
            # workers = celery.control.inspect()
            # SLOW WAY
            # active_tasks = workers.active()
            # revoked_tasks = workers.revoked()
            # reserved_tasks = workers.reserved()
            # scheduled_tasks = workers.scheduled()
            # SLOW WAY
            # if active_tasks is None:
            #     active_tasks = []
            # if revoked_tasks is None:
            #     revoked_tasks = []
            # if scheduled_tasks is None:
            #     scheduled_tasks = []
            # if reserved_tasks is None:
            #     reserved_tasks = []

            log.verbose('listing items')
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    if task_id is not None and task["id"] != task_id:
                        continue

                    row = {}
                    row['status'] = 'ACTIVE'
                    row['worker'] = worker
                    row['ETA'] = task["time_start"]
                    row['task_id'] = task["id"]
                    row['task'] = task["name"]
                    row['args'] = task["args"]

                    if task_id is not None:
                        task_result = celery.AsyncResult(task_id)
                        row['task_status'] = task_result.status
                        row['info'] = task_result.info
                    data.append(row)

            for worker, tasks in revoked_tasks.items():
                for task in tasks:
                    if task_id is not None and task != task_id:
                        continue
                    row = {}
                    row['status'] = 'REVOKED'
                    row['task_id'] = task
                    data.append(row)

            for worker, tasks in scheduled_tasks.items():
                for task in tasks:
                    if task_id is not None and \
                       task["request"]["id"] != task_id:
                        continue

                    row = {}
                    row['status'] = 'SCHEDULED'
                    row['worker'] = worker
                    row['ETA'] = task["eta"]
                    row['task_id'] = task["request"]["id"]
                    row['priority'] = task["priority"]
                    row['task'] = task["request"]["name"]
                    row['args'] = task["request"]["args"]
                    data.append(row)

            for worker, tasks in reserved_tasks.items():
                for task in tasks:
                    if task_id is not None and \
                       task["id"] != task_id:
                        continue

                    data.append({
                        'status': 'SCHEDULED',
                        'worker': worker,
                        'ETA': task['time_start'],
                        'task_id': task["id"],
                        'priority': task['delivery_info']["priority"],
                        'task': task["name"],
                        'args': task["args"],
                    })

            # from celery.task.control import inspect
            # tasks = inspect()
            log.verbose('listing completed')

            return self.force_response(data)

        def put(self, task_id):
            celery = self.get_service_instance('celery')
            celery.control.revoke(task_id)
            return self.empty_response()

        def delete(self, task_id):
            celery = self.get_service_instance('celery')
            celery.control.revoke(task_id, terminate=True)
            return self.empty_response()
