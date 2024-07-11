from src.concerns.moderation import ModerationPromptsOperationNames


def test_all_moderation_prompts_configured_are_described():
    assert len(ModerationPromptsOperationNames.list()) == 1
    assert ModerationPromptsOperationNames.MODERATION.value == "moderation"
