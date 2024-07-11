import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

import src.proto.embed_jobs_pb2 as embed_jobs_pb2
from src.schemas.endpoints.responses import HTTPValidationResponse

from .api.api import api_router
from .api.v1.api import api_router as api_v1_router
from .core.config import get_settings
from .core.containers import container
from .exceptions.base import BaseException, base_exception_handler
from .exceptions.http import custom_validation_exception_handler
from .jobs.embed_job import EmbedJob

settings = get_settings()
prefix = settings.API_PREFIX
prefix_v1 = prefix + settings.API_V1_PREFIX

logging.basicConfig(level=settings.LOG_LEVEL)

# Wire Container
container.wire(packages=[__package__])

app = FastAPI(title=settings.APP_NAME)
app.include_router(api_router, prefix=prefix)
app.include_router(
    api_v1_router,
    prefix=prefix_v1,
    responses={422: {"model": HTTPValidationResponse}},
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return custom_validation_exception_handler(request, exc)


@app.exception_handler(BaseException)
def custom_app_exception_handler(request, e):
    return base_exception_handler(request, e)


@app.on_event("startup")
def on_startup():
    consumer = container.kafka_consumer()
    consumer.subscribe(
        [
            [
                settings.KAFKA_EMBED_JOBS_TOPIC,
                embed_jobs_pb2.ArticleNotification,
                EmbedJob(container.kafka_producer()).run,
            ]
        ]
    )
    consumer.start()


@app.on_event("shutdown")
def shutdown_event():
    container.kafka_producer().close()
    container.kafka_consumer().close()
