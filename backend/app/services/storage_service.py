import asyncio
import uuid

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from app.config import settings

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _get_s3_client():
    if not settings.AWS_ENDPOINT_URL_S3:
        return None
    return boto3.client(
        "s3",
        endpoint_url=settings.AWS_ENDPOINT_URL_S3,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=BotoConfig(signature_version="s3v4"),
    )


def generate_file_key(dossier_id: uuid.UUID, document_type: str, file_name: str) -> str:
    ext = file_name.rsplit(".", 1)[-1] if "." in file_name else "bin"
    return f"dossiers/{dossier_id}/{document_type}/{uuid.uuid4().hex}.{ext}"


async def upload_file(file_key: str, file_data: bytes, content_type: str) -> bool:
    client = _get_s3_client()
    if not client:
        return False
    try:
        await asyncio.to_thread(
            client.put_object,
            Bucket=settings.BUCKET_NAME,
            Key=file_key,
            Body=file_data,
            ContentType=content_type,
        )
        return True
    except ClientError:
        return False


async def get_presigned_url(file_key: str, expires_in: int = 3600) -> str | None:
    client = _get_s3_client()
    if not client:
        return None
    try:
        return await asyncio.to_thread(
            client.generate_presigned_url,
            "get_object",
            Params={"Bucket": settings.BUCKET_NAME, "Key": file_key},
            ExpiresIn=expires_in,
        )
    except ClientError:
        return None


async def delete_file(file_key: str) -> bool:
    client = _get_s3_client()
    if not client:
        return False
    try:
        await asyncio.to_thread(
            client.delete_object, Bucket=settings.BUCKET_NAME, Key=file_key
        )
        return True
    except ClientError:
        return False


async def download_file(file_key: str) -> bytes | None:
    client = _get_s3_client()
    if not client:
        return None
    try:
        response = await asyncio.to_thread(
            client.get_object, Bucket=settings.BUCKET_NAME, Key=file_key
        )
        return response["Body"].read()
    except ClientError:
        return None


def validate_file(content_type: str, size: int) -> str | None:
    if content_type not in ALLOWED_MIME_TYPES:
        return f"Tipo de archivo no permitido: {content_type}. Permitidos: PDF, JPEG, PNG, WebP"
    if size > MAX_FILE_SIZE:
        return f"Archivo demasiado grande: {size} bytes. Maximo: {MAX_FILE_SIZE // (1024 * 1024)} MB"
    return None
