# Pluck the requirements
FROM python:3.11-slim as requirements-stage
WORKDIR /tmp
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


# --------------------------------------------------------------------------------------------------------
# Initial build with virtualenv
FROM python:3.11-slim as build

# Turns off writing .pyc files; superfluous on an ephemeral container.
ENV PYTHONDONTWRITEBYTECODE=1
# Seems to speed things up
ENV PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    build-essential gcc

WORKDIR /app
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY --from=requirements-stage /tmp/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt


# --------------------------------------------------------------------------------------------------------
# Final image
FROM python:3.11-slim

# Run stuff as non-root user
RUN groupadd -g 999 python && \
    useradd -r -u 999 -g python python

RUN mkdir /app && chown python:python /app
WORKDIR /app

COPY --chown=python:python --from=build /venv /venv
COPY --chown=python:python ./src ./src
COPY --chown=python:python ./alembic ./alembic
COPY --chown=python:python ./alembic.ini ./alembic.ini

# Get the release string from the build args
ARG release_string="dev"
ENV RELEASE_STRING=$release_string

ENV PATH="/venv/bin:$PATH"

# Run server
CMD python -m gunicorn -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:80 src.main:app