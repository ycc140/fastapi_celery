# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2023-08-27 14:34:48
     $Rev: 46
"""

# Local modules
from ..config.setup import config

resource_example = {
    "name": "ProcessingService",
    "status": True,
    "version": "1.4.2",
    "resources": [
        {
            "name": "Celery.broker (RabbitMq)",
            "status": True
        },
        {
            "name": "Celery.backend (MongoDb)",
            "status": True
        },
        {
            "name": "Celery.worker (celery@e7dc920209c7)",
            "status": True
        },
        {
            "name": "Celery.worker (celery@CHARON)",
            "status": True
        }
    ]
}

status_example = {
    "status": "SUCCESS",
    "result": {"message": "Lots of work was done here", "value": 3}
}

process_example = {
    "status": "PENDING",
    "id": "94624ffb-d5e8-4fbb-a760-dbdef0abb46f"
}

retry_example = {
    "status": "PENDING",
    "task_id": "9a8e43a6-be5b-41da-8cd1-b6ba78222417",
    "failed_id": "94624ffb-d5e8-4fbb-a760-dbdef0abb46f"
}

process_request_body_example = {
    "queue": {
        "summary": "responseQueue",
        "value": {"msg": "test-01 today",
                  "responseQueue": "CallerService"}},
    "url": {
        "summary": "responseUrl",
        "value": {"msg": "test-02 today",
                  "responseUrl": "http://localhost:8001/v1/response"}},
    "docker": {
        "summary": "local Docker responseUrl",
        "value": {"msg": "test-03 today",
                  "responseUrl": "http://host.docker.internal:8001/v1/response"}}
}

tags_metadata = [
    {
        "name": "Process endpoints",
        "description": f"The ***{config.service_name}*** handle processing of long-time running tasks.",
    },
    {
        "name": "Health endpoint",
        "description": "Checks connection status for all Celery workers.",
    }
]

license_info = {
    "name": "License: Apache 2.0",
    "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
}

description = """
<img width="25%" align="right" src="/static/architecture.png"/>
**This is a Microservice template that illustrates how to use Celery tasks
and callbacks to keep a responsive API regardless of processing time.**

**The following architectural components are used:**

**Docker**
    *Docker is containerization technology that enables the creation and use of Linux containers.*

**Flower**
    *Flower is an open-source web application for monitoring and managing Celery clusters.
    It provides real-time information about the status of Celery workers and tasks.*

**Celery**
    *Celery is a simple, flexible, and reliable distributed system to process vast amounts of messages,
    while providing operations with the tools required to maintain such a system.*

**RabbitMQ**
    *RabbitMQ is a messaging broker - an intermediary for messaging. It gives your applications
    a common platform to send and receive messages, and your messages a safe place to live until received.*

**MongoDB**
    *MongoDB is an open source NoSQL database management program that can manage document-oriented information.*

**Uvicorn**
    *Uvicorn is an ASGI web server implementation for Python.*

**Gunicorn**
    *Gunicorn 'Green Unicorn' is a Python WSGI HTTP Server for UNIX. It is used in front of Uvicorn to make 
    sure the defined number of workers are always running.*
    
**FastAPI**
    *FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+
    based on standard Python type hints.*

**Prism**
    *Prism is an open-source HTTP mock and proxy server.*
    
<br>**The following HTTP status codes are returned:**
  * `200:` Successful GET response.
  * `202:` Successful POST response.
  * `400:` Task ID has the wrong state for a retry (not FAILED).
  * `404:` Task ID not found in DB.
  * `422:` Validation error, supplied parameter(s) are incorrect.
  * `500:` Failed Health response.
  * `500:` Failed Celery task initialisation.
<br><br>
---
"""
