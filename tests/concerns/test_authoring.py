from src.concerns.authoring import AuthoringPromptsOperationNames


# Test all prompts in described in the config schema are implemented
def test_all_prompts_configured_are_described(make_prompt_templates_plain):
    assert len(AuthoringPromptsOperationNames.list()) == len(
        make_prompt_templates_plain()
    )
    assert AuthoringPromptsOperationNames.FIX_GRAMMAR.value == "fix-grammar"
    assert AuthoringPromptsOperationNames.SUMMARIZE.value == "summarize"
    assert (
        AuthoringPromptsOperationNames.SUMMARIZE_INTO_STEPS.value
        == "summarize-into-steps"
    )
    assert AuthoringPromptsOperationNames.CHANGE_TONE.value == "change-tone"
    assert AuthoringPromptsOperationNames.TRANSLATE.value == "translate"
    assert (
        AuthoringPromptsOperationNames.IMPROVE_WRITING.value
        == "improve-writing"
    )
    assert (
        AuthoringPromptsOperationNames.REDUCE_READING_COMPLEXITY.value
        == "reduce-reading-complexity"
    )
    assert AuthoringPromptsOperationNames.list() == [
        "fix-grammar",
        "summarize",
        "summarize-into-steps",
        "change-tone",
        "translate",
        "improve-writing",
        "reduce-reading-complexity",
        "reduce-reading-time",
        "expand-writing",
    ]
