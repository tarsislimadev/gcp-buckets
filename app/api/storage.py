from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.services.storage import GCPStorageService

router = APIRouter(prefix="/api", tags=["storage"])


class UploadUrlRequest(BaseModel):
    blob_name: str = Field(min_length=1)
    content_type: str = Field(min_length=1)


class SignedUrlResponse(BaseModel):
    url: str
    expires_in_minutes: int


@lru_cache
def get_storage_service() -> GCPStorageService:
    settings = get_settings()
    return GCPStorageService()


@router.get("/buckets", response_model=list[str])
def list_buckets(service: GCPStorageService = Depends(get_storage_service)) -> list[str]:
    return service.list_buckets()


@router.get("/buckets/{bucket_name}/files")
def list_files(
    bucket_name: str,
    prefix: str = Query(default=""),
    service: GCPStorageService = Depends(get_storage_service),
) -> dict:
    return service.list_files(bucket_name, prefix)


@router.post("/buckets/{bucket_name}/upload-url", response_model=SignedUrlResponse)
def create_upload_url(
    bucket_name: str,
    request: UploadUrlRequest,
    service: GCPStorageService = Depends(get_storage_service),
) -> SignedUrlResponse:
    expiration = get_settings().signed_url_expiration_minutes
    return SignedUrlResponse(
        url=service.generate_upload_signed_url(
            bucket_name, request.blob_name, request.content_type, expiration
        ),
        expires_in_minutes=expiration,
    )


@router.get("/buckets/{bucket_name}/download-url", response_model=SignedUrlResponse)
def create_download_url(
    bucket_name: str,
    blob_name: str = Query(min_length=1),
    service: GCPStorageService = Depends(get_storage_service),
) -> SignedUrlResponse:
    expiration = get_settings().signed_url_expiration_minutes
    return SignedUrlResponse(
        url=service.generate_download_signed_url(bucket_name, blob_name, expiration),
        expires_in_minutes=expiration,
    )


@router.delete("/buckets/{bucket_name}/files", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    bucket_name: str,
    blob_name: str = Query(min_length=1),
    service: GCPStorageService = Depends(get_storage_service),
) -> None:
    try:
        service.delete_file(bucket_name, blob_name)
    except Exception as exc:
        raise HTTPException(status_code=404, detail="File could not be deleted") from exc