from src.domain.aggregates.category import Category
from src.domain.repositories.category_repository import CategoryRepository


async def handle_list_categories(
    category_repo: CategoryRepository,
) -> list[Category]:
    categories = await category_repo.get_all_active()
    return categories
