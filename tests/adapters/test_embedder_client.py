import json
from unittest.mock import call, patch

import pytest
from cohere_sagemaker.embeddings import Embedding, Embeddings

from src.adapters.embedder_client import (
    CohereEmbedderClient,
    SagemakerEmbedderClient,
)


@patch("src.adapters.embedder_client.Client.embed")
def test_cohere_embedder_calls_endpoint(embed_mock, check_log_message):
    embed_mock.return_value = Embeddings([Embedding([1, 2, 3])])
    embedder = CohereEmbedderClient("us-east-1", "test_name")
    check_log_message("INFO", "Cohere Embedder Client initialized")

    embedder._connected = True
    embedder.embed("test text")
    embed_mock.assert_called_once_with(texts=["test text"])

    # Not gonna show since connection is mocked
    # check_log_message(
    #     "INFO", 'Cohere Embedder Client connected to "test_name"'
    # )
    check_log_message(
        "INFO", f"Creating embeddings for: {json.dumps(['test text'])}"
    )
    check_log_message("INFO", "Embeddings created")


@patch("src.adapters.embedder_client.Client.embed")
def test_cohere_embedder_calls_endpoint_with_list(embed_mock):
    embed_mock.return_value = Embeddings([Embedding([1, 2, 3])])
    embedder = CohereEmbedderClient("us-east-1", "test_name")
    embedder._connected = True
    embedder.embed(["test text", "test text 2"])
    embed_mock.assert_called_once_with(texts=["test text", "test text 2"])


def test_cohere_embedder_raises_with_empty():
    embedder = CohereEmbedderClient("us-east-1", "test_name")
    embedder._connected = True
    with pytest.raises(ValueError):
        embedder.embed("")


@patch("src.adapters.embedder_client.Predictor.predict")
def test_sagemaker_embedder_calls_endpoint(predict_mock, check_log_message):
    predict_mock.return_value = '{"embedding": [0.1, 0.2, 0.3]}'
    embedder = SagemakerEmbedderClient("test_name")
    check_log_message("INFO", "Sagemaker Embedder Client initialized")

    embedder.embed("test text")
    predict_mock.assert_called_once_with(
        "test text",
        {"ContentType": "application/x-text", "Accept": "application/json"},
    )

    check_log_message(
        "INFO", f"Creating embeddings for: {json.dumps(['test text'])}"
    )
    check_log_message("INFO", "Embeddings created")


@patch("src.adapters.embedder_client.Predictor.predict")
def test_sagemaker_embedder_calls_endpoint_multiple_times(predict_mock):
    predict_mock.return_value = '{"embedding": [0.1, 0.2, 0.3]}'
    embedder = SagemakerEmbedderClient("test_name")
    embedder.embed(["test text", "test text 2"])
    predict_mock.assert_has_calls(
        [
            call(
                "test text",
                {
                    "ContentType": "application/x-text",
                    "Accept": "application/json",
                },
            ),
            call(
                "test text 2",
                {
                    "ContentType": "application/x-text",
                    "Accept": "application/json",
                },
            ),
        ]
    )


def test_sagemaker_embedder_raises_with_empty():
    embedder = SagemakerEmbedderClient("test_name")
    with pytest.raises(ValueError):
        embedder.embed("")
