from ...adapters.embedder_client import (
    BedrockEmbedderClient,
    CohereEmbedderClient,
    HuggingFaceSagemakerEmbedderClient,
)


def get_embedder(endpoint_type: str, endpoint_name: str, aws_region: str):
    embedder = None
    match endpoint_type:
        case "cohere_embedder":
            embedder = CohereEmbedderClient(
                region=aws_region,
                endpoint_name=endpoint_name,
            )
        case "huggingface_embedder":
            embedder = HuggingFaceSagemakerEmbedderClient(
                endpoint_name=endpoint_name
            )
        case "bedrock_embedder":
            embedder = BedrockEmbedderClient(
                service_name="bedrock-runtime",
                region_name=aws_region,
                endpoint_url=f"https://bedrock-runtime."
                f"{aws_region}.amazonaws.com",
                model_id=endpoint_name,
                accept="application/json",
                content_type="application/json",
            )
    if embedder is None:
        embedder = HuggingFaceSagemakerEmbedderClient(
            endpoint_name=endpoint_name
        )
    return embedder
