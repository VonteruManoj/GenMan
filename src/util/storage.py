import json

import boto3

from src.contracts.storage import StorageInterface


class S3Storage(StorageInterface):
    def __init__(
        self,
        client: boto3.client,
        bucket: str | None = None,
    ):
        self._client = client
        self.bucket = bucket

    def get_file(self, key: str, bucket: str | None = None) -> any:
        """Get file from a S3 bucket

        Parameters
        ----------
        key : str
            File path
        bucket : str | None, optional
            Bucket name, by default None

        Returns
        -------
        any

        Raises
        ------
        ValueError
            If bucket name is not provided
        """

        _bucket = bucket or self.bucket
        if not _bucket:
            raise ValueError("Bucket name is not provided")

        key = key.lstrip("/")

        result = self._client.get_object(Bucket=_bucket, Key=key)

        return result["Body"].read().decode("utf-8")

    def get_json(self, key: str, bucket: str | None = None) -> dict:
        """Get a JSON from a S3 bucket

        Parameters
        ----------
        key : str
            File path
        bucket : str | None, optional
            Bucket name, by default None

        Returns
        -------
        dict

        Raises
        ------
        ValueError
            If bucket name is not provided
        """

        return json.loads(self.get_file(key, bucket))

    def put_file(self, key: str, data: any, bucket: str | None = None) -> None:
        """Set file in a S3 bucket

        Parameters
        ----------
        key : str
            File path
        data : any
            File data
        bucket : str | None, optional
            Bucket name, by default None

        Raises
        ------
        ValueError
            If bucket name is not provided
        """

        _bucket = bucket or self.bucket
        if not _bucket:
            raise ValueError("Bucket name is not provided")

        key = key.lstrip("/")

        self._client.put_object(Bucket=_bucket, Key=key, Body=data)

    def put_json(
        self, key: str, data: dict, bucket: str | None = None
    ) -> None:
        """Set a JSON in a S3 bucket

        Parameters
        ----------
        key : str
            File path
        data : dict
            JSON data
        bucket : str | None, optional
            Bucket name, by default None

        Raises
        ------
        ValueError
            If bucket name is not provided
        """

        self.put_file(key, json.dumps(data), bucket)

    def list_files(
        self, bucket: str | None = None, prefix: str = ""
    ) -> list[str]:
        """List files in a S3 bucket

        Parameters
        ----------
        bucket : str | None, optional
            Bucket name, by default None
        prefix : str | None, optional
            Prefix of the files, by default None

        Returns
        -------
        list[str]

        Raises
        ------
        ValueError
            If bucket name is not provided
        """

        _bucket = bucket or self.bucket
        if not _bucket:
            raise ValueError("Bucket name is not provided")

        result = self._client.list_objects_v2(Bucket=_bucket, Prefix=prefix)

        if "Contents" not in result:
            return []
        return [obj["Key"] for obj in result["Contents"]]

    def delete_file(self, key: str, bucket: str | None = None) -> None:
        """Delete file in a S3 bucket

        Parameters
        ----------
        key : str
            File path
        data : any
            File data
        bucket : str | None, optional
            Bucket name, by default None

        Raises
        ------
        ValueError
            If bucket name is not provided
        """

        _bucket = bucket or self.bucket
        if not _bucket:
            raise ValueError("Bucket name is not provided")

        key = key.lstrip("/")

        self._client.delete_object(Bucket=_bucket, Key=key)
