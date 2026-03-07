from fastapi import APIRouter, Depends

from src.api.dependencies.repositories import get_category_repo
from src.api.schemas.category import CategoryResp, ListCategoriesResp
from src.application.handlers.list_categories_handler import handle_list_categories
from src.domain.repositories.category_repository import CategoryRepository

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=ListCategoriesResp)
async def list_categories(
    category_repo: CategoryRepository = Depends(get_category_repo),
) -> ListCategoriesResp:
    categories = await handle_list_categories(category_repo=category_repo)
    items = [CategoryResp.from_domain(c) for c in categories]
    return ListCategoriesResp(items=items, total=len(items))
