from functools import lru_cache

import boto3

from src.core.config import get_settings

from .logger import get_logger


@lru_cache()
def get_session(
    aws_access_key_id: str, aws_secret_access_key: str, region_name: str
):
    """Get boto3 session.

    If the environment is local, the AWS_LOCALSTACK_URL is set and any of the
    necessary credential is None, then the session is created with fake
    credentials.

    Parameters
    ----------
    aws_access_key_id : str
        AWS access key ID
    aws_secret_access_key : str
        AWS secret access key
    region_name : str
        AWS region name

    Returns
    -------
    boto3.session.Session
        Boto3 session
    """

    settings = get_settings()

    if (
        (aws_access_key_id is None or aws_secret_access_key is None)
        and settings.APP_ENV == "local"
        and settings.AWS_LOCALSTACK_URL is not None
    ):
        get_logger(__name__).debug("[LocalStack] AWS Session mocked in local")
        return boto3.session.Session(
            aws_access_key_id="fake-key-id",
            # deepcode ignore HardcodedNonCryptoSecret: this is not a secret
            # but a fake key, needed in the signature; this is only used in
            # local environment for localstack
            aws_secret_access_key="fake-access-key",
            # deepcode ignore HardcodedNonCryptoSecret: this is not a secret
            # but a fake key, needed in the signature; this is only used in
            # local environment for localstack
            region_name=region_name,
        )

    get_logger(__name__).debug("[AWS] Setting session")
    return boto3.session.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
    )


@lru_cache()
def get_client(session: boto3.session.Session, service_name: str):
    """Get boto3 client.

    If the environment is local, the AWS_LOCALSTACK_URL is set and any of the
    necessary credential is None, then the client is pointed to localstack
    endpoint.

    Parameters
    ----------
    session : boto3.session.Session
        Boto3 session
    service_name : str
        AWS service name

    Returns
    -------
    boto3.client
        Boto3 client
    """

    settings = get_settings()

    if (
        (
            settings.AWS_ACCESS_KEY_ID is None
            or settings.AWS_SECRET_ACCESS_KEY is None
        )
        and settings.APP_ENV == "local"
        and settings.AWS_LOCALSTACK_URL is not None
    ):
        get_logger(__name__).debug(
            f"[LocalStack] {service_name} mocked in local"
        )
        return session.client(
            service_name=service_name, endpoint_url=settings.AWS_LOCALSTACK_URL
        )

    get_logger(__name__).debug(f"[AWS] {service_name} client created")
    return session.client(service_name=service_name)
