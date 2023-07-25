# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2023-07-25 07:27:21
     $Rev: 44
"""

# Third party modules
from starlette.testclient import TestClient

# local modules
from ..src.config.setup import CommonConfig, DockerLocal, DockerProd


# ---------------------------------------------------------
#
def test_dev_config(test_app: TestClient):
    """ Test DEV config.

    :param test_app: TestClient instance.
    """

    conf = CommonConfig()

    assert conf.flower_host == 'localhost'
    assert isinstance(conf.hdr_data, dict)
    assert isinstance(conf.url_timeout, tuple)
    assert conf.hdr_data['X-API-Key'] == conf.service_api_key


# ---------------------------------------------------------
#
def test_local_config(test_app: TestClient):
    """ Test LOCAL config.

    :param test_app: TestClient instance.
    """

    _root_config = CommonConfig()
    _docker_env = DockerLocal().model_dump()
    conf = _root_config.model_copy(update=_docker_env)

    assert conf.flower_host == 'dashboard'


# ---------------------------------------------------------
#
def test_prod_config(test_app: TestClient):
    """ Test PROD config.

    :param test_app: TestClient instance.
    """

    _root_config = CommonConfig()
    _docker_env = DockerProd().model_dump()
    conf = _root_config.model_copy(update=_docker_env)

    assert conf.log_level == 'info'
    assert conf.log_diagnose == False
    assert conf.flower_host == 'dashboard'
