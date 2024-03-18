# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2024-03-18 22:09:25
     $Rev: 1
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

    with TestClient(app) as test_client:
        yield test_client
