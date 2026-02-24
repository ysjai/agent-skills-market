from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import Response

from src.api.dependencies.auth import get_current_user
from src.api.dependencies.repositories import get_blob_repo
from src.api.schemas.blob import UploadBlobResp
from src.application.handlers.create_blob_handler import handle_create_blob
from src.application.handlers.get_blob_handler import handle_get_blob
from src.domain.aggregates.user import User
from src.domain.repositories.blob_repository import BlobRepository

router = APIRouter(prefix="/blobs", tags=["blobs"])


@router.post("", response_model=UploadBlobResp, status_code=status.HTTP_201_CREATED)
async def upload_blob(
    file: UploadFile,
    blob_repo: BlobRepository = Depends(get_blob_repo),
    current_user: User = Depends(get_current_user),
    compress: bool = True,
) -> UploadBlobResp:
    content = await file.read()
    blob = await handle_create_blob(
        content=content,
        compress=compress,
        blob_repo=blob_repo,
    )
    return UploadBlobResp.from_domain(blob)


@router.put("/{blob_id}", response_model=UploadBlobResp)
async def update_blob(
    blob_id: str,
    file: UploadFile,
    blob_repo: BlobRepository = Depends(get_blob_repo),
    current_user: User = Depends(get_current_user),
    compress: bool = True,
) -> UploadBlobResp:
    content = await file.read()
    blob = await handle_create_blob(
        content=content,
        compress=compress,
        blob_repo=blob_repo,
    )
    return UploadBlobResp.from_domain(blob)


@router.get("/{blob_id}")
async def download_blob(
    blob_id: str,
    content_type: str | None = None,
    blob_repo: BlobRepository = Depends(get_blob_repo),
    current_user: User = Depends(get_current_user),
) -> Response:
    blob = await handle_get_blob(
        blob_id=UUID(blob_id),
        blob_repo=blob_repo,
    )
    media_type = content_type or "application/octet-stream"
    return Response(
        content=blob.get_raw_content(),
        media_type=media_type,
    )
