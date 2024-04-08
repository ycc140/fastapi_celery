# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2024-04-08 17:11:52
     $Rev: 7
"""

# local modules
from src import CommonConfig, DockerLocal, DockerProd


# ---------------------------------------------------------
#
def test_dev_config():
    """ Test DEV config. """
    conf = CommonConfig()

    assert conf.flower_host == 'localhost'
    assert isinstance(conf.hdr_data, dict)
    assert isinstance(conf.url_timeout, tuple)
    assert conf.hdr_data['X-API-Key'] == conf.service_api_key


# ---------------------------------------------------------
#
def test_local_config():
    """ Test LOCAL config. """
    _docker_env = DockerLocal().model_dump()
    conf = CommonConfig().model_copy(update=_docker_env)

    assert conf.flower_host == 'dashboard'
    assert conf.hdr_data['X-API-Key'] == conf.service_api_key


# ---------------------------------------------------------
#
def test_prod_config():
    """ Test PROD config. """
    _docker_env = DockerProd().model_dump()
    conf = CommonConfig().model_copy(update=_docker_env)

    assert conf.log_level == 'info'
    assert conf.log_diagnose is False
    assert conf.flower_host == 'dashboard'
    assert conf.hdr_data['X-API-Key'] == conf.service_api_key
