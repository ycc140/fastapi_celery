# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2023-07-25 06:54:49
     $Rev: 43
"""

# BUILTIN modules
import site
from os import environ
from pathlib import Path
from typing import Type, Tuple

# Third party modules
from pydantic import BaseModel, computed_field
from pydantic_settings import (PydanticBaseSettingsSource,
                               BaseSettings, SettingsConfigDict)

# Constants
MISSING_ENV = '>>> missing ENV value <<<'
""" Error message for missing values in the .env file. """
MISSING_SECRET = '>>> missing SECRETS file <<<'
""" Error message for missing secrets file. """
SECRETS_DIR = ('/run/secrets'
               if Path('/.dockerenv').exists()
               else f'{site.USER_BASE}/secrets')
""" This is where your secrets are stored (in Docker or locally). """
ENVIRONMENT = environ.get('ENVIRONMENT', 'dev')
""" Current platform environment. """


# -----------------------------------------------------------------------------
#
class CommonConfig(BaseSettings):
    """ Configuration parameters used by all environments.

    These values are populated in the following order; content of the
    .env file and different secrets files. No environment values are read.
    """
    model_config = SettingsConfigDict(secrets_dir=SECRETS_DIR,
                                      env_file_encoding='utf-8',
                                      env_file=Path(__file__).parent / '.env')

    # project
    name: str = MISSING_ENV
    version: str = MISSING_ENV
    service_name: str = MISSING_ENV

    # Logging and environment dependable parameters.
    log_level: str = MISSING_ENV
    log_format: str = MISSING_ENV
    flower_host: str = MISSING_ENV
    log_diagnose: bool = MISSING_ENV

    # External resource parameters.
    mongo_url: str = MISSING_SECRET
    rabbit_url: str = MISSING_SECRET
    service_api_key: str = MISSING_SECRET

    # Hardcoded REST method (GET, POST) calling parameters.
    url_timeout: tuple = (1.0, 5.0)

    @computed_field
    @property
    def hdr_data(self) -> dict:
        """ Use a defined secret as a value. """
        return {'Content-Type': 'application/json',
                'X-API-Key': f'{self.service_api_key}'}

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: Type[BaseSettings],
            env_settings: PydanticBaseSettingsSource,
            init_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """ Change source priority order (ignore environment values). """
        return init_settings, dotenv_settings, file_secret_settings


# -----------------------------------------------------------------------------
#
class DockerLocal(BaseModel):
    """ Configuration parameters unique for Docker local environment.

    No environment values, .env or secrets files are read in this class.

    These values will override the values in the CommonConfig class.
    """

    # Changes due to Docker context.
    flower_host: str = 'dashboard'


# -----------------------------------------------------------------------------
#
class DockerProd(BaseModel):
    """ Configuration parameters unique for Docker production environment.

    No environment values, .env or secrets files are read in this class.

    These values will override the values in the CommonConfig class.
    """

    # Changes due to Docker context.
    flower_host: str = 'dashboard'

    # Avoid excessive logs.
    log_level: str = 'info'

    # Disable display of sensitive error dump values in the log.
    log_diagnose: bool = False


# ---------------------------------------------------------

# Translation between Docker environment and their classes.
_setup = {'local': DockerLocal, 'prod': DockerProd}

if ENVIRONMENT == 'dev':
    config = CommonConfig()

else:
    _root_config = CommonConfig()
    _docker_env = _setup[ENVIRONMENT]().model_dump()
    config = _root_config.model_copy(update=_docker_env)
