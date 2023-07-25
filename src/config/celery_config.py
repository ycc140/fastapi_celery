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

# Local modules
from .setup import config

# ---------------------------------------------------------

# Broker settings.
broker_url = config.rabbit_url

# Using the database to store task state and results.
result_backend = f'{config.mongo_url}service_results'

# Add input parameters to backend result.
result_extended = True

# List of modules to import when the Celery
# worker starts (improves start time).
imports = ('src.tasks',)

# Normalize logging format.
worker_log_format = '%(asctime)s | %(levelname)-8s | %(processName)s | %(message)s'
worker_task_log_format = '%(asctime)s | %(levelname)-8s | %(processName)s | ' \
                         '%(task_name)s[%(task_id)s] | %(message)s'

# Decrease the message rates substantially.
worker_send_task_event = False

## task will be killed after 60 seconds
# task_time_limit = 60

## task will raise exception SoftTimeLimitExceeded after 50 seconds.
# task_soft_time_limit = 50

## task messages will be acknowledged after the task has been executed,
## not just before (the default behavior).
# task_acks_late = True

# One worker takes 10 tasks from queue at a time
# and will increase the performance.
worker_prefetch_multiplier = 10
