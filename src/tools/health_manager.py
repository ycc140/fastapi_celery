# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2023-07-15 13:49:23
     $Rev: 20
"""

# BUILTIN modules
from typing import List

# Third party modules
from loguru import logger
from httpx import AsyncClient, ConnectTimeout


# local modules
from ..config.setup import config
from ..api.models import ResourceModel, HealthResponseModel


# ---------------------------------------------------------
#
async def _get_celery_status() -> List[ResourceModel]:
    """ Return Celery worker(s) connection status.

    :return: Celery worker(s) connection status.
    """

    result = []
    host = config.flower_host

    try:
        async with AsyncClient() as client:
            url = f"http://{host}:5555/api/workers?status=true"
            resp = await client.get(timeout=config.url_timeout,
                                    url=url, headers=config.hdr_data)

        if resp.status_code != 200:
            errmsg = f"Failed GET request for URL {url} - " \
                     f"[{resp.status_code}: {resp.json()['detail']}]."
            raise RuntimeError(errmsg)

        for worker, status in resp.json().items():
            result += [ResourceModel(name=worker, status=status)]

    except ConnectTimeout as why:
        logger.error(f'WORKER: {why}')
        result += [ResourceModel(name='Celery', status=False)]

    return result


# ---------------------------------------------------------
#
async def get_health_status() -> HealthResponseModel:
    """ Return Health status for used resources.

    :return: Service health status.
    """
    resource_items = []
    resource_items += await _get_celery_status()
    total_status = (all(key.status for key in resource_items)
                    if resource_items else False)

    return HealthResponseModel(status=total_status,
                               version=config.version,
                               name=config.service_name,
                               resources=resource_items)
