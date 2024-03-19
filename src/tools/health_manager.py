# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2024-03-19 20:02:51
     $Rev: 4
"""

# BUILTIN modules
from typing import List
from pathlib import Path
from datetime import date

# Third party modules
import aiofiles
from loguru import logger

# local modules
from ..tasks import WORKER
from ..config.setup import config
from ..api.models import ResourceModel, HealthResponseModel

# Constants
CERT_EXPIRE_FILE = (
        Path(__file__).parent.parent.parent / 'certs' / 'expire-date.txt'
)
""" File containing certificate expiry date. """


# ---------------------------------------------------------
#
async def _get_certificate_remaining_days() -> int:
    """ Return SSL certificate remaining valid days.

    Will return 0 if the cert expires-date file is missing,
    or an invalid ISO 8601 date format (YYYY-MM-DD) is found.

    :return: Remaining valid days.
    """
    try:
        async with aiofiles.open(CERT_EXPIRE_FILE, mode='r') as cert:
            raw_date = await cert.read()

        remaining_days = date.fromisoformat(raw_date) - date.today()
        return remaining_days.days

    except (EnvironmentError, ValueError):
        return 0


# ---------------------------------------------------------
#
def _get_certificate_status(remaining_days: int) -> List[ResourceModel]:
    """ Return SSL certificate validity status.

    :return: Certificate validity status.
    """
    return [ResourceModel(name='Certificate.valid',
                          status=remaining_days > 0)]


# ---------------------------------------------------------
#
async def _get_celery_main_status() -> List[ResourceModel]:
    """ Return Celery RabbitMQ broker and MongoDB backend connection status.

    :return: Celery broker and backend connection status.
    """
    result = []

    try:
        with WORKER.connection_for_write() as conn:
            conn.connect()
            conn.release()
            broker_state = True

    except Exception as why:
        logger.error(f'BROKER: {why}')
        broker_state = False

    result += [ResourceModel(name='Celery.broker (RabbitMq)', status=broker_state)]

    try:
        # noinspection PyProtectedMember
        WORKER.backend._get_connection().server_info()
        backend_state = True

    except Exception as why:
        logger.error(f'BACKEND: {why}')
        backend_state = False

    result += [ResourceModel(name='Celery.backend (MongoDb)', status=backend_state)]

    return result


# ---------------------------------------------------------
#
async def get_celery_worker_status() -> List[ResourceModel]:
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

    except Exception as why:
        logger.error(f'WORKER: {why}')
        result += [ResourceModel(name='Celery.worker', status=False)]

    return result


# ---------------------------------------------------------
#
async def get_health_status() -> HealthResponseModel:
    """ Return Health status for used resources.

    :return: Service health status.
    """
    resource_items = []
    days = await _get_certificate_remaining_days()
    resource_items += _get_certificate_status(days)
    resource_items += await _get_celery_main_status()
    resource_items += await get_celery_worker_status()
    total_status = (all(key.status for key in resource_items)
                    if resource_items else False)

    return HealthResponseModel(status=total_status,
                               version=config.version,
                               name=config.service_name,
                               resources=resource_items,
                               cert_remaining_days=days)
