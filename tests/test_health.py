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

# Third party modules
import pytest
from starlette.testclient import TestClient
from httpx import AsyncClient, ASGITransport

# local modules
from ..src.tools.health_manager import get_celery_worker_status


# ---------------------------------------------------------
#
@pytest.mark.anyio
async def test_health(test_app: TestClient):
    """ Test successful or failed health endpoint.

    :param test_app: TestClient instance.
    """
    transport = ASGITransport(app=test_app.app)
    worker_status = await get_celery_worker_status()

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    # The Celery worker is started.
    if worker_status[0].status is True:
        assert response.status_code == 200
        assert response.json()['status'] is True

    else:
        assert response.status_code == 500
        assert response.json()['status'] is False
