from datetime import timedelta
from typing import Any

from google.cloud import storage


class GCPStorageService:
    def __init__(self, client: storage.Client | None = None) -> None:
        self.client = client or storage.Client()

    def list_buckets(self) -> list[str]:
        return [bucket.name for bucket in self.client.list_buckets()]

    def list_files(self, bucket_name: str, prefix: str = "") -> dict[str, list[dict[str, Any]] | list[str]]:
        bucket = self.client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefix, delimiter="/")
        folders: set[str] = set()
        files: list[dict[str, Any]] = []

        for page in blobs.pages:
            folders.update(page.prefixes)
            for blob in page:
                if blob.name == prefix:
                    continue
                files.append(
                    {
                        "name": blob.name,
                        "size": blob.size,
                        "content_type": blob.content_type,
                        "updated": blob.updated.isoformat() if blob.updated else None,
                    }
                )

        return {"folders": sorted(folders), "files": files}

    def generate_download_signed_url(
        self, bucket_name: str, blob_name: str, expiration_minutes: int = 15
    ) -> str:
        blob = self.client.bucket(bucket_name).blob(blob_name)
        return blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="GET",
        )

    def generate_upload_signed_url(
        self,
        bucket_name: str,
        blob_name: str,
        content_type: str,
        expiration_minutes: int = 15,
    ) -> str:
        blob = self.client.bucket(bucket_name).blob(blob_name)
        return blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="PUT",
            content_type=content_type,
        )

    def delete_file(self, bucket_name: str, blob_name: str) -> None:
        self.client.bucket(bucket_name).blob(blob_name).delete()