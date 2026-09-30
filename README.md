# GCP Storage Manager

FastAPI foundation for browsing Google Cloud Storage buckets and performing browser-friendly file operations through signed URLs.

## Run locally

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`. Interactive OpenAPI documentation is available at `/docs`.

For local Google Cloud authentication, set `GOOGLE_APPLICATION_CREDENTIALS` in `.env` or use Application Default Credentials. In production on Cloud Run, prefer the service account attached to the service instead of a JSON key.

## API surface

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Service health check |
| `GET` | `/api/buckets` | List accessible buckets |
| `GET` | `/api/buckets/{bucket}/files?prefix=folder/` | List files and simulated folders |
| `POST` | `/api/buckets/{bucket}/upload-url` | Create a signed `PUT` URL |
| `GET` | `/api/buckets/{bucket}/download-url?blob_name=...` | Create a signed `GET` URL |
| `DELETE` | `/api/buckets/{bucket}/files?blob_name=...` | Delete a file |

Upload URL request body:

```json
{"blob_name": "documents/report.pdf", "content_type": "application/pdf"}
```

The browser must send the same `Content-Type` header when using the returned signed upload URL. Configure the bucket's CORS policy for the frontend origin before enabling direct browser uploads.

## Scope

This initial slice covers the storage core API from the implementation roadmap. Authentication/RBAC, database metadata, audit events, previews, and the frontend explorer remain follow-up phases. The service layer accepts an injected GCS client, so those endpoints can be tested with a fake client without contacting GCP.

## Docker

```bash
docker build -t gcp-storage-manager .
docker run --rm -p 8000:8000 --env-file .env gcp-storage-manager
```