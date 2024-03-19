# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2024-03-19 20:45:39
     $Rev: 5
"""

# Third party modules
import pytest
from starlette.testclient import TestClient

# Local program modules
from ..src.main import app


# ---------------------------------------------------------
#
@pytest.fixture(scope="module")
def anyio_backend():
    """ Module fixture. """

    return 'asyncio'


# ---------------------------------------------------------
#
@pytest.fixture(scope="module")
def test_app():
    """ Module fixture. """

    with TestClient(app=app) as test_client:
        yield test_client
