
# -------------------------------------
# first stage
#
FROM python:alpine AS build

# set work directory
WORKDIR /usr/src/app

# Use argument parameter to build for test, stage or prod environment
ARG BUILD_ENV

# PYTHONUNBUFFERED=1        => make sure all messages always reach console
# PYTHONDONTWRITEBYTECODE=1 => don't generate byte code
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

# install system dependencies
RUN apk upgrade

# install python dependencies
RUN pip install --upgrade pip setuptools wheel
COPY ../requirements_${BUILD_ENV}.txt ./requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

# -------------------------------------
# second stage
#
FROM python:alpine

# create the appropriate directories and define current timezone
ENV APP_HOME=/home/awd TZ=Europe/Stockholm

# create the app user and update system dependencies
RUN set -eux; \
    addgroup -g 1000 awd; \
    adduser -u 1000 -G awd awd -D; \
    # Upgrade the package index and install security upgrades
    apk update; \
    apk upgrade; \
    rm -rf /var/lib/apk/lists/*; \
    # Set local timezone (needs to be done before changing user).
    ln -snf /usr/share/zoneinfo/"$TZ" /etc/localtime && echo "$TZ" > /etc/timezone

# Copy created wheels from build stage
COPY --from=build /usr/src/app/wheels /wheels

# Install python dependencies
RUN set -eux; \
    pip install --no-cache --upgrade pip; \
    pip install --no-cache /wheels/*; \
    rm -rf /wheels

# set work directory
WORKDIR $APP_HOME

# copy project and chown all the files to the app user
COPY src $APP_HOME/src

# copy client certificates to the app user
COPY certs $APP_HOME/certs

# Update gunicorn and uvicorn log level based on log file configurationand build env.
RUN ["python", "src/config/create_external_config.py"]

# change to the app user
USER awd
