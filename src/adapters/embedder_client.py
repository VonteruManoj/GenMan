import json
from typing import List, Optional

import boto3
from cohere_sagemaker import Client
from sagemaker import Predictor
from sagemaker.deserializers import JSONDeserializer
from sagemaker.serializers import JSONSerializer

from src.contracts.embedder import EmbedderInterface
from src.core.deps.logger import with_logger


@with_logger()
class CohereEmbedderClient(EmbedderInterface):
    def __init__(self, region: str, endpoint_name: str):
        self._client = Client(region_name=region)
        self._endpoint_name = endpoint_name
        self._connected = False
        self._logger.info("Cohere Embedder Client initialized")

    def connect(self):
        self._client.connect_to_endpoint(endpoint_name=self._endpoint_name)
        self._connected = True
        self._logger.info(
            "Cohere Embedder Client connected"
            f" to {json.dumps(self._endpoint_name)}"
        )

    def embed(self, text: str | List[str]) -> List[List[float]]:
        if not self._connected:
            self.connect()
        if not text:
            raise ValueError("Text cannot be empty.")
        if isinstance(text, str):
            text = [text]
        self._logger.info(f"Creating embeddings for: {json.dumps(text)}")
        response = self._client.embed(texts=text)
        embeddings = [e for e in response.embeddings]
        self._logger.info("Embeddings created")
        return embeddings

    @property
    def connected(self) -> bool:
        return self._connected


@with_logger()
class SagemakerEmbedderClient(EmbedderInterface):
    def __init__(self, endpoint_name: str):
        self.predictor = Predictor(
            endpoint_name=endpoint_name,
        )
        self._connected = True
        self._logger.info("Sagemaker Embedder Client initialized")

    def connect(self):
        pass

    def embed(self, text: str | List[str]) -> List[float]:
        if not text:
            raise ValueError("Text cannot be empty.")
        if isinstance(text, str):
            text = [text]
        self._logger.info(f"Creating embeddings for: {json.dumps(text)}")
        embeddings = []
        for t in text:
            response = self.predictor.predict(
                t,
                {
                    "ContentType": "application/x-text",
                    "Accept": "application/json",
                },
            )
            response = json.loads(response)
            embeddings.append(response["embedding"])
        self._logger.info(
            "Embeddings created: "
            f"{json.dumps({'input': text, 'output': embeddings})}"
        )
        return embeddings

    @property
    def connected(self) -> bool:
        return self._connected


@with_logger()
class HuggingFaceSagemakerEmbedderClient(EmbedderInterface):
    def __init__(self, endpoint_name: str):
        self.predictor = Predictor(
            endpoint_name=endpoint_name,
            serializer=JSONSerializer(),
            deserializer=JSONDeserializer(),
        )
        self._connected = True

    def cls_pooling(self, model_output):
        # first element of model_output contains all token embeddings
        return [sublist[0] for sublist in model_output][0]

    def connect(self):
        pass

    class huggingface_serializer:
        def __init__(self, tokenizer, max_length):
            self.tokenizer = tokenizer
            self.max_length = max_length

        def __call__(self, text):
            return self.tokenizer(
                text,
                padding="max_length",
                truncation=True,
                max_length=self.max_length,
                return_tensors="pt",
            )

    def embed(self, snippets: str | List[str]) -> List[Optional[List[float]]]:
        if not snippets:
            raise ValueError("Text cannot be empty.")
        if isinstance(snippets, str):
            snippets = [snippets]
        embeddings = []
        for snippet in snippets:
            vector = None
            try:
                inp = {"inputs": snippet}
                results = self.predictor.predict(inp)
                vector = self.cls_pooling(results)
            except Exception as e:
                self._logger.error(e)
            embeddings.append(vector)
        return embeddings

    @property
    def connected(self) -> bool:
        return self._connected


@with_logger()
class BedrockEmbedderClient(EmbedderInterface):
    def __init__(
        self,
        service_name: str,
        region_name: str,
        endpoint_url: str,
        model_id: str,
        accept: str,
        content_type: str,
    ):
        self.predictor = boto3.client(
            service_name=service_name,
            region_name=region_name,
            endpoint_url=endpoint_url,
        )
        self.modelId = model_id
        self.accept = accept
        self.contentType = content_type
        self._connected = True

    def connect(self):
        pass

    def embed(self, snippets: str | List[str]) -> List[Optional[List[float]]]:
        if not snippets:
            raise ValueError("Text cannot be empty.")
        if isinstance(snippets, str):
            snippets = [snippets]

        embeddings = []
        for snippet in snippets:
            embedding = None
            try:
                inp = {"inputText": snippet}

                response = self.predictor.invoke_model(
                    modelId=self.modelId,
                    contentType=self.contentType,
                    accept=self.accept,
                    body=json.dumps(inp),
                )
                response_body = json.loads(response.get("body").read())
                embedding = response_body.get("embedding")
            except Exception as e:
                self._logger.error(e)
            embeddings.append(embedding)
        return embeddings

    @property
    def connected(self) -> bool:
        return self._connected
