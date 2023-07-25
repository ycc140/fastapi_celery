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
import os
import json
from os import environ
from pathlib import Path
from configparser import ConfigParser

# Constants.
CWD = Path(__file__).parent
""" Defines the current working directory. """
BUILD = environ.get('BUILD_ENV')
""" Current platform environment. """
ADJUSTED_LEVELS = {'TRACE': 'DEBUG', 'SUCCESS': 'INFO'}
""" Adjusted log levels for gunicorn. """


# -----------------------------------------------------------------------------
#
class DockerApiConfigManager:
    """
    This class handles the creating of uvicorn and gunicorn log config files
    based on the environment and the content of the .env file.

    When the Docker build environment is LOCAL an uvicorn.json is created
    from the config/uvicorn.template file updated with the log level from
    the global log config file.

    When the Docker build environment is PROD a gunicorn.conf is created
    from the config/gunicorn.template file updated with the log level
    from the global log config file.


    @ivar config: Configuration parameters.
    """

    # ---------------------------------------------------------
    #
    def __init__(self, conf: callable):
        """ Class initializer.

        :param conf: Configuration parameters.
        """

        self.config = conf

    # ---------------------------------------------------------
    #
    def _create_uvicorn_file(self):
        """ Create an uvicorn.json log configuration file.

        Create a new uvicorn log config file based upon the uvicorn template
        file, updated with the log level from the global log config file for
        all available loggers.
        """

        level = self.config.log_level.upper()

        # Get uvicorn log template reference.
        with open(f"{CWD}/uvicorn.template") as hdl:
            template = json.load(hdl)

        # Set current log level from global log configuration.
        for item in ('uvicorn.error', 'uvicorn.access'):

            # Make sure any loggers exist before trying an update.
            if 'loggers' in template and item in template['loggers']:
                template['loggers'][item]['level'] = level

        # Store updated uvicorn log configuration.
        with open(f'{CWD.parent.parent}/uvicorn.json', 'w') as hdl:
            json.dump(template, hdl, indent=4)

    # ---------------------------------------------------------
    #
    def _create_gunicorn_file(self):
        """ Create a gunicorn.conf log configuration file.

        Create a new gunicorn log config file based upon the gunicorn template
        file, updated with the log level from the global log config file for
        all available loggers.
        """

        ini_config = ConfigParser()
        level = self.config.log_level.upper()

        # Get gunicorn log template reference.
        ini_config.read(f"{CWD}/gunicorn.template")

        # Set current log level from global log configuration.
        for section in ('logger_root',
                        'logger_gunicorn.error',
                        'logger_gunicorn.access'):

            # gunicorn only accepts default python log levels, so we
            # need to handle the extra log levels that Loguru have defined.
            if section in ini_config:
                ini_config.set(section, 'level',
                               ADJUSTED_LEVELS.get(level, level))

        # Store updated gunicorn log configuration.
        with open(f'{CWD.parent.parent}/gunicorn.conf', 'w') as hdl:
            ini_config.write(hdl)

    # ---------------------------------------------------------
    #
    def create_config_files(self):
        """ Create uvicorn and gunicorn log configuration files.

        Create a new uvicorn log config file based upon the uvicorn template
        file updated with the log level from the global log config file.

        Create a new gunicorn log config file based upon the gunicorn template
        file updated with the log level from the global log config file.
        """

        if BUILD == 'prod':
            self._create_gunicorn_file()

        else:
            self._create_uvicorn_file()


# ---------------------------------------------------------

if __name__ == '__main__':
    # For config to work here we have to set the
    # environment BEFORE we import the config module.
    os.environ['ENVIRONMENT'] = BUILD

    from setup import config

    DockerApiConfigManager(config).create_config_files()
