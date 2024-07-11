LONG_PROMPT_TEMPLATE = (
    "This is a very long template with {{context}} and {{question}}"
)
SHORT_PROMPT_TEMPLATE = (
    "This is a short template with {{context}} and {{question}}"
)

PARAMS = {
    "param1": "value1",
}

SUMMARIZER_CONFIG_TEMPLATE = {
    "templates": {
        "long": LONG_PROMPT_TEMPLATE,
        "short": SHORT_PROMPT_TEMPLATE,
    },
    "falcon_params": PARAMS,
    "llama2_params": PARAMS,
    "cohere_params": PARAMS,
    "bedrock_params": PARAMS,
}
