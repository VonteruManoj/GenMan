import copy

BASE_PROMPT = {
    "platform": "OpenAI",
    "model": "davinci",
    "temperature": 0.5,
    "top_p": 0.8,
    "max_tokens": 160,
    "disabled": False,
}

COMPLETION_PROMPT = copy.deepcopy(BASE_PROMPT) | {
    "prompt": "Fix spelling and grammatical errors,"
    ' ignore words between "#":\n\n{{text}}'
}

CHAT_COMPLETION_PROMPT = copy.deepcopy(BASE_PROMPT) | {
    "messages": [
        {
            "role": "system",
            "content": "You are a summarizer. If you find words"
            ' surrounded by "#", they should be outputted the'
            " same way and should always be in the output."
            " Your answer should never have hashtags.",
        },
        {"role": "user", "content": "Shorten the text:\n\n{{text}}"},
    ]
}

CHAT_COMPLETION_CHANGE_TONE_PROMPT = copy.deepcopy(BASE_PROMPT) | {
    "messages": [
        {"role": "system", "content": "Change the tone"},
        {"role": "user", "content": "Change to {{tone}}:\n\n{{text}}"},
    ]
}

CHAT_COMPLETION_TRANSLATE_PROMPT = copy.deepcopy(BASE_PROMPT) | {
    "messages": [
        {"role": "system", "content": "Translate"},
        {"role": "user", "content": "Translate to {{language}}:\n\n{{text}}"},
    ]
}

CHAT_COMPLETION_IMPROVE_WRITING_PROMPT = copy.deepcopy(BASE_PROMPT) | {
    "messages": [
        {"role": "system", "content": "Fix writitng"},
        {"role": "user", "content": "Fix me please:\n\n{{text}}"},
    ]
}

CHAT_COMPLETION_REDUCE_READING_COMPLEXITY_PROMPT = copy.deepcopy(
    BASE_PROMPT
) | {
    "messages": [
        {"role": "system", "content": "Simplifier"},
        {"role": "user", "content": "Simplify this:\n\n{{text}}"},
    ]
}

CHAT_COMPLETION_REDUCE_READING_TIME_PROMPT = copy.deepcopy(BASE_PROMPT) | {
    "messages": [
        {"role": "system", "content": "Reduce time"},
        {"role": "user", "content": "Reduce time this:\n\n{{text}}"},
    ]
}

CHAT_COMPLETION_EXPAND_WRITING_PROMPT = copy.deepcopy(BASE_PROMPT) | {
    "messages": [
        {"role": "system", "content": "Expand writing"},
        {"role": "user", "content": "Expand writing of this:\n\n{{text}}"},
    ]
}

PROMPT_TEMPLATES = {
    "FixGrammar": copy.deepcopy(COMPLETION_PROMPT),
    "Summarize": copy.deepcopy(CHAT_COMPLETION_PROMPT),
    "SummarizeIntoSteps": copy.deepcopy(CHAT_COMPLETION_PROMPT),
    "ChangeTone": copy.deepcopy(CHAT_COMPLETION_CHANGE_TONE_PROMPT),
    "Translate": copy.deepcopy(CHAT_COMPLETION_TRANSLATE_PROMPT),
    "ImproveWriting": copy.deepcopy(CHAT_COMPLETION_IMPROVE_WRITING_PROMPT),
    "ReduceReadingComplexity": copy.deepcopy(
        CHAT_COMPLETION_REDUCE_READING_COMPLEXITY_PROMPT
    ),
    "ReduceReadingTime": copy.deepcopy(
        CHAT_COMPLETION_REDUCE_READING_TIME_PROMPT
    ),
    "ExpandWriting": copy.deepcopy(CHAT_COMPLETION_EXPAND_WRITING_PROMPT),
}
