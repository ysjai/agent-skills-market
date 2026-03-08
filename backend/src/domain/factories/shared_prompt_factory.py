from uuid import UUID
from src.domain.aggregates.shared_prompt import SharedPrompt


class SharedPromptFactory:
    @staticmethod
    def create(
        prompt_id: UUID,
        user_id: UUID,
        share_message: str | None = None,
    ) -> SharedPrompt:
        return SharedPrompt(
            prompt_id=prompt_id,
            user_id=user_id,
            share_message=share_message,
        )
