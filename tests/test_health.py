# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2023-07-15 12:48:23
     $Rev: 19
"""

# Third party modules
import pytest
from httpx import AsyncClient
from starlette.testclient import TestClient

# This is the same as using the @pytest.mark.anyio
# on all test functions in the module
pytestmark = pytest.mark.anyio


# ---------------------------------------------------------
#
async def test_normal_health(test_app: TestClient):
    """ Test successful health endpoint.

    :param test_app: TestClient instance.
    """

    async with AsyncClient(app=test_app.app, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()['status'] is True
