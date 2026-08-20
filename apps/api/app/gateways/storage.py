"""S3-compatible object storage gateway.

Documento 02 (secao 7 - Storage) exige uma abstracao S3-compatible, valida
para Cloudflare R2, AWS S3 e MinIO local, sem que o restante da aplicacao
dependa de um provider especifico de storage.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import BinaryIO

import boto3
from botocore.client import Config as BotoConfig

from app.core.config import get_settings


@dataclass
class StoredObject:
    storage_key: str
    bucket: str
    size_bytes: int
    content_type: str | None = None


class StorageGateway:
    """Thin abstraction over an S3-compatible object store."""

    def __init__(self) -> None:
        settings = get_settings()
        self._bucket = settings.storage_bucket
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.storage_endpoint,
            aws_access_key_id=settings.storage_access_key,
            aws_secret_access_key=settings.storage_secret_key,
            region_name=settings.storage_region,
            config=BotoConfig(
                signature_version="s3v4",
                s3={"addressing_style": "path" if settings.storage_use_path_style else "auto"},
            ),
        )

    def ensure_bucket(self) -> None:
        existing = {b["Name"] for b in self._client.list_buckets().get("Buckets", [])}
        if self._bucket not in existing:
            self._client.create_bucket(Bucket=self._bucket)

    def put_object(
        self, storage_key: str, fileobj: BinaryIO, content_type: str | None = None
    ) -> StoredObject:
        extra_args = {"ContentType": content_type} if content_type else {}
        self._client.upload_fileobj(fileobj, self._bucket, storage_key, ExtraArgs=extra_args)
        head = self._client.head_object(Bucket=self._bucket, Key=storage_key)
        return StoredObject(
            storage_key=storage_key,
            bucket=self._bucket,
            size_bytes=head["ContentLength"],
            content_type=head.get("ContentType"),
        )

    def get_presigned_url(self, storage_key: str, expires_in: int = 3600) -> str:
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": storage_key},
            ExpiresIn=expires_in,
        )

    def delete_object(self, storage_key: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=storage_key)

    def object_exists(self, storage_key: str) -> bool:
        try:
            self._client.head_object(Bucket=self._bucket, Key=storage_key)
            return True
        except self._client.exceptions.ClientError:
            return False
