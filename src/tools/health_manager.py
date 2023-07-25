# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2023-07-24 19:41:02
     $Rev: 41
"""

# BUILTIN modules
from typing import List

# Third party modules
from loguru import logger

# local modules
from ..tasks import WORKER
from ..config.setup import config
from ..api.models import ResourceModel, HealthResponseModel


# ---------------------------------------------------------
#
async def _get_celery_worker_status() -> List[ResourceModel]:
    """ Return Celery worker(s) connection status.

    :return: Celery worker(s) connection status.
    """

    result = []

    try:
        if items := WORKER.control.ping(timeout=0.1):

            for worker in [key for elem in items for key in elem.keys()]:
                result += [ResourceModel(name=f'Celery.worker ({worker})', status=True)]

        else:
            logger.error('No active workers found.')
            result += [ResourceModel(name='Celery.worker', status=False)]

    except BaseException as why:
        logger.error(f'WORKER: {why}')
        result += [ResourceModel(name='Celery.worker', status=False)]

    return result


# ---------------------------------------------------------
#
async def _get_celery_main_status() -> list:
    """ Return Celery RabbitMQ broker and MongoDB backend connection status.

    :return: Celery broker and backend connection status.
    """

    result = []

    try:
        with WORKER.connection_for_write() as conn:
            conn.connect()
            conn.release()
            broker_state = True

    except BaseException as why:
        logger.error(f'BROKER: {why}')
        broker_state = False

    result += [ResourceModel(name='Celery.broker (RabbitMq)', status=broker_state)]

    try:
        # noinspection PyProtectedMember
        WORKER.backend._get_connection().server_info()
        backend_state = True

    except BaseException as why:
        logger.error(f'BACKEND: {why}')
        backend_state = False

    result += [ResourceModel(name='Celery.backend (MongoDb)', status=backend_state)]

    return result


# ---------------------------------------------------------
#
async def get_health_status() -> HealthResponseModel:
    """ Return Health status for used resources.

    :return: Service health status.
    """
    resource_items = []
    resource_items += await _get_celery_main_status()
    resource_items += await _get_celery_worker_status()
    total_status = (all(key.status for key in resource_items)
                    if resource_items else False)

    return HealthResponseModel(status=total_status,
                               version=config.version,
                               name=config.service_name,
                               resources=resource_items)
