from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.repositories import get_blob_repo, get_tree_repo
from app.api.schemas.tree import (
    AddTreeFileReq,
    AddTreeFileResp,
    BatchUploadReq,
    BatchUploadResp,
    CreateTreeReq,
    CreateTreeResp,
    DeleteTreeFileReq,
    FolderUploadReq,
    GetTreeResp,
    MoveTreeFileReq,
    RenameTreeFileReq,
    UpdateTreeFileContentReq,
)
from app.application.handlers.add_tree_file_handler import handle_add_tree_file
from app.application.handlers.create_tree_handler import handle_create_tree
from app.application.handlers.delete_tree_file_handler import handle_delete_tree_file
from app.application.handlers.get_tree_handler import handle_get_tree
from app.application.handlers.move_tree_file_handler import handle_move_tree_file
from app.application.handlers.rename_tree_file_handler import handle_rename_tree_file
from app.application.handlers.update_tree_file_content_handler import (
    handle_update_tree_file_content,
)
from app.domain.aggregates.user import User
from app.domain.repositories.blob_repository import BlobRepository
from app.domain.repositories.tree_repository import TreeRepository

router = APIRouter(prefix="/trees", tags=["trees"])


@router.post("", response_model=CreateTreeResp, status_code=status.HTTP_201_CREATED)
async def create_tree(
    request: CreateTreeReq,
    tree_repo: TreeRepository = Depends(get_tree_repo),
    current_user: User = Depends(get_current_user),
) -> CreateTreeResp:
    tree = await handle_create_tree(
        entries=request.entries,
        tree_repo=tree_repo,
    )
    return CreateTreeResp.from_domain(tree)


@router.get("/{tree_id}", response_model=GetTreeResp)
async def get_tree(
    tree_id: UUID,
    tree_repo: TreeRepository = Depends(get_tree_repo),
    current_user: User = Depends(get_current_user),
) -> GetTreeResp:
    tree = await handle_get_tree(
        tree_id=tree_id,
        tree_repo=tree_repo,
    )
    return GetTreeResp.from_domain(tree)


@router.post("/{tree_id}/files", response_model=AddTreeFileResp)
async def add_file(
    tree_id: UUID,
    request: AddTreeFileReq,
    tree_repo: TreeRepository = Depends(get_tree_repo),
    blob_repo: BlobRepository = Depends(get_blob_repo),
    current_user: User = Depends(get_current_user),
) -> AddTreeFileResp:
    tree = await handle_add_tree_file(
        tree_id=tree_id,
        path=request.path,
        entry_type=request.entry_type,
        blob_id=request.blob_id,
        content=request.content,
        tree_repo=tree_repo,
        blob_repo=blob_repo,
    )
    return AddTreeFileResp.from_domain(tree)


@router.delete("/{tree_id}/files", response_model=CreateTreeResp)
async def delete_file(
    tree_id: UUID,
    request: DeleteTreeFileReq | None = None,
    path: str | None = None,
    tree_repo: TreeRepository = Depends(get_tree_repo),
    blob_repo: BlobRepository = Depends(get_blob_repo),
    current_user: User = Depends(get_current_user),
) -> CreateTreeResp:
    delete_path = request.path if request else path
    if not delete_path:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Path is required")
    tree = await handle_delete_tree_file(
        tree_id=tree_id,
        path=delete_path,
        tree_repo=tree_repo,
        blob_repo=blob_repo,
    )
    return CreateTreeResp.from_domain(tree)


@router.put("/{tree_id}/files/rename", response_model=CreateTreeResp)
async def rename_file(
    tree_id: UUID,
    request: RenameTreeFileReq,
    tree_repo: TreeRepository = Depends(get_tree_repo),
    current_user: User = Depends(get_current_user),
) -> CreateTreeResp:
    tree = await handle_rename_tree_file(
        tree_id=tree_id,
        old_path=request.old_path,
        new_path=request.new_path,
        tree_repo=tree_repo,
    )
    return CreateTreeResp.from_domain(tree)


@router.put("/{tree_id}/files/move", response_model=CreateTreeResp)
async def move_file(
    tree_id: UUID,
    request: MoveTreeFileReq,
    tree_repo: TreeRepository = Depends(get_tree_repo),
    current_user: User = Depends(get_current_user),
) -> CreateTreeResp:
    tree = await handle_move_tree_file(
        tree_id=tree_id,
        source=request.source,
        target=request.target,
        tree_repo=tree_repo,
    )
    return CreateTreeResp.from_domain(tree)


@router.put("/{tree_id}/files/content", response_model=CreateTreeResp)
async def update_file_content(
    tree_id: UUID,
    request: UpdateTreeFileContentReq,
    tree_repo: TreeRepository = Depends(get_tree_repo),
    blob_repo: BlobRepository = Depends(get_blob_repo),
    current_user: User = Depends(get_current_user),
) -> CreateTreeResp:
    tree = await handle_update_tree_file_content(
        tree_id=tree_id,
        path=request.path,
        content=request.content,
        tree_repo=tree_repo,
        blob_repo=blob_repo,
    )
    return CreateTreeResp.from_domain(tree)


@router.post("/{tree_id}/files/batch", response_model=BatchUploadResp)
async def batch_upload(
    tree_id: UUID,
    request: BatchUploadReq,
    tree_repo: TreeRepository = Depends(get_tree_repo),
    blob_repo: BlobRepository = Depends(get_blob_repo),
    current_user: User = Depends(get_current_user),
) -> BatchUploadResp:
    """Batch upload files to a tree."""
    uploaded = 0
    failed = 0
    for entry in request.entries:
        try:
            await handle_add_tree_file(
                tree_id=tree_id,
                path=entry.path,
                entry_type=entry.entry_type,
                blob_id=None,
                content=entry.content,
                tree_repo=tree_repo,
                blob_repo=blob_repo,
            )
            uploaded += 1
        except Exception:
            failed += 1
    return BatchUploadResp(uploaded=uploaded, failed=failed)


@router.post("/{tree_id}/files/folder", response_model=AddTreeFileResp)
async def upload_folder(
    tree_id: UUID,
    request: FolderUploadReq,
    tree_repo: TreeRepository = Depends(get_tree_repo),
    blob_repo: BlobRepository = Depends(get_blob_repo),
    current_user: User = Depends(get_current_user),
) -> AddTreeFileResp:
    """Upload files to a folder in a tree."""
    for entry in request.entries:
        if request.base_path:
            full_path = f"{request.base_path}/{entry.path}"
        else:
            full_path = entry.path
        await handle_add_tree_file(
            tree_id=tree_id,
            path=full_path,
            entry_type=entry.entry_type,
            blob_id=entry.blob_id,
            content=entry.content,
            tree_repo=tree_repo,
            blob_repo=blob_repo,
        )
    tree = await handle_get_tree(tree_id=tree_id, tree_repo=tree_repo)
    return AddTreeFileResp.from_domain(tree)
