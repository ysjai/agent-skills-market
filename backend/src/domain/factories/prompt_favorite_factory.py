from uuid import UUID
from src.domain.aggregates.prompt_favorite import PromptFavorite
from src.domain.aggregates.prompt import Prompt


class PromptFavoriteFactory:
    @staticmethod
    def create(
        user_id: UUID,
        shared_prompt_id: UUID,
        prompt: Prompt,
        author,  # User object
    ) -> PromptFavorite:
        return PromptFavorite(
            user_id=user_id,
            shared_prompt_id=shared_prompt_id,
            snapshot_title=prompt.title,
            snapshot_content=prompt.content,
            snapshot_description=prompt.description,
            snapshot_tags=list(prompt.tags),
            snapshot_author_name=author.username,
            snapshot_version=prompt.version,
        )
