from src.adapters.summarizer_client import (
    BedrockSummarizerClient,
    CohereSummarizerClient,
    FalconSummarizerClient,
    Llama2SummarizerClient,
)
from src.contracts.repositories.assets import AssetsRepositoryInterface


def get_summarizer(
    assets_repo: AssetsRepositoryInterface,
    endpoint_type: str,
    endpoint_name: str,
    aws_region: str,
    config_filename: str,
    prompt_type: str,
):
    summarizer = None
    match endpoint_type:
        case "bedrock_summarizer":
            summarizer = BedrockSummarizerClient(
                assets_repo=assets_repo,
                region=aws_region,
                endpoint_name=endpoint_name,
                config_filename=config_filename,
                prompt_type=prompt_type,
            )
        case "cohere_summarizer":
            summarizer = CohereSummarizerClient(
                assets_repo=assets_repo,
                region=aws_region,
                endpoint_name=endpoint_name,
                config_filename=config_filename,
                prompt_type=prompt_type,
            )
        case "huggingface_summarizer":
            if "llama-2" in endpoint_name:
                summarizer = Llama2SummarizerClient(
                    assets_repo=assets_repo,
                    endpoint_name=endpoint_name,
                    config_filename=config_filename,
                    prompt_type=prompt_type,
                )
            elif "falcon-7b" in endpoint_name:
                summarizer = FalconSummarizerClient(
                    assets_repo=assets_repo,
                    endpoint_name=endpoint_name,
                    config_filename=config_filename,
                    prompt_type=prompt_type,
                )
    if summarizer is None:
        summarizer = Llama2SummarizerClient(
            assets_repo=assets_repo,
            endpoint_name=endpoint_name,
            config_filename=config_filename,
            prompt_type=prompt_type,
        )

    return summarizer
