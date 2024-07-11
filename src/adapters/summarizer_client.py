import json
from typing import List

import boto3
from cohere_sagemaker import Client
from sagemaker.deserializers import JSONDeserializer
from sagemaker.predictor import Predictor

from src.builders.prompts import SemanticSearchSummarizePrompt
from src.contracts.repositories.assets import AssetsRepositoryInterface
from src.contracts.summarizer import SummarizerInterface


class SummarizerClient(SummarizerInterface):
    def __init__(self, assets_repo: AssetsRepositoryInterface):
        self._assets_repo = assets_repo


class FalconSummarizerClient(SummarizerClient):
    def __init__(
        self,
        assets_repo: AssetsRepositoryInterface,
        endpoint_name: str,
        config_filename: str,
        prompt_type: str,
    ):
        super().__init__(assets_repo)
        self.predictor = Predictor(
            endpoint_name=endpoint_name,
            deserializer=JSONDeserializer(),
            timeout=600,
        )
        self._endpoint_name = endpoint_name
        self._connected = True
        config = self._assets_repo.get_json_asset(config_filename)
        self._templates = config["templates"]
        self._params = config["falcon_params"]
        self._prompt_type = prompt_type
        self._prompt_builder = SemanticSearchSummarizePrompt()
        self._prompt_builder.template = self._templates[self._prompt_type]

    def connect(self):
        pass

    @property
    def connected(self):
        return self._connected

    def summarize(self, context: str | List[str], question: str) -> str:
        if not context:
            raise ValueError("Context cannot be empty.")
        if not question:
            raise ValueError("Question cannot be empty.")
        if isinstance(context, list):
            context = " ".join(context)
        prompt = self._prompt_builder.build(context, question)
        payload = {
            "inputs": prompt,
            "parameters": self._params,
        }
        payload = json.dumps(payload)
        payload = payload.encode("utf-8")
        response = self.predictor.predict(
            payload,
            initial_args={"ContentType": "application/json"},
            custom_attributes="accept_eula=true",
        )
        return response[0]["generated_text"][len(prompt) :]  # noqa: E203


class Llama2SummarizerClient(SummarizerClient):
    def __init__(
        self,
        assets_repo: AssetsRepositoryInterface,
        endpoint_name: str,
        config_filename: str,
        prompt_type: str,
    ):
        super().__init__(assets_repo)
        self.predictor = Predictor(
            endpoint_name=endpoint_name, deserializer=JSONDeserializer()
        )
        self._endpoint_name = endpoint_name
        self._connected = True
        config = self._assets_repo.get_json_asset(config_filename)
        self._templates = config["templates"]
        self._params = config["llama2_params"]
        self._prompt_type = prompt_type
        self._prompt_builder = SemanticSearchSummarizePrompt()
        self._prompt_builder.template = self._templates[self._prompt_type]

    def connect(self):
        pass

    @property
    def connected(self):
        return self._connected

    def summarize(self, context: str | List[str], question) -> str:
        if not context:
            raise ValueError("Context cannot be empty.")
        if not question:
            raise ValueError("Question cannot be empty.")
        if isinstance(context, list):
            context = " ".join(context)
        prompt = self._prompt_builder.build(context, question)
        payload = {
            "inputs": [
                [
                    {"role": "system", "content": prompt},
                    {
                        "role": "user",
                        "content": question,
                    },
                ]
            ],
            "parameters": self._params,
        }
        payload = json.dumps(payload)
        payload = payload.encode("utf-8")
        response = self.predictor.predict(
            payload,
            initial_args={
                "ContentType": "application/json",
            },
            custom_attributes="accept_eula=true",
        )
        print(response)
        return response[0]["generation"]["content"]


class CohereSummarizerClient(SummarizerClient):
    def __init__(
        self,
        assets_repo: AssetsRepositoryInterface,
        region: str,
        endpoint_name: str,
        config_filename: str,
        prompt_type: str,
    ):
        super().__init__(assets_repo)
        self._client = Client(region_name=region)
        self._endpoint_name = endpoint_name
        self._connected = False
        config = self._assets_repo.get_json_asset(config_filename)
        self._templates = config["templates"]
        self._params = config["cohere_params"]
        self._prompt_type = prompt_type
        self._prompt_builder = SemanticSearchSummarizePrompt()
        self._prompt_builder.template = self._templates[self._prompt_type]

    def connect(self):
        self._client.connect_to_endpoint(endpoint_name=self._endpoint_name)
        self._connected = True

    def summarize(self, context: str | List[str], question) -> str:
        if not context:
            raise ValueError("Context cannot be empty.")
        if not question:
            raise ValueError("Question cannot be empty.")
        if isinstance(context, list):
            context = " ".join(context)
        if not self._connected:
            self.connect()
        prompt = self._prompt_builder.build(context, question)
        response = self._client.generate(
            prompt=prompt,
            **self._params,
        )
        return response.generations[0].text

    @property
    def connected(self) -> bool:
        return self._connected


class BedrockSummarizerClient(SummarizerClient):
    def __init__(
        self,
        assets_repo: AssetsRepositoryInterface,
        endpoint_name: str,
        region: str,
        config_filename: str,
        prompt_type: str,
    ):
        super().__init__(assets_repo)
        config = self._assets_repo.get_json_asset(config_filename)
        self._params = config["bedrock_params"]
        self._region = config["region"]
        self.predictor = boto3.client(
            service_name="bedrock-runtime",
            region_name=config["region"],
            endpoint_url=f"https://bedrock-runtime."
            f"{self._region}.amazonaws.com",
        )
        self._endpoint_name = endpoint_name
        self._connected = True
        self._templates = config["templates"]
        self._prompt_type = prompt_type
        self._prompt_builder = SemanticSearchSummarizePrompt()
        self._prompt_builder.template = self._templates[self._prompt_type]

    def connect(self):
        pass

    def summarize(self, context: str | List[str], question) -> str:
        if not context:
            raise ValueError("Context cannot be empty.")
        if not question:
            raise ValueError("Question cannot be empty.")
        if isinstance(context, list):
            context = " ".join(context)

        result_key = ""
        result_subkeys = None

        prompt = self._prompt_builder.build(context, question)
        payload = {"inputText": prompt}

        if "titan" in self._params["modelId"]:
            result_key = "results"
            result_subkeys = ["outputText"]
        elif "anthropic" in self._params["modelId"]:
            result_key = "completion"
            payload = {
                "prompt": f"Human: {prompt}\n\nAssistant:",
                "max_tokens_to_sample": 300,
            }
        elif "ai21" in self._params["modelId"]:
            result_key = "completions"
            result_subkeys = ["data", "text"]

        payload = json.dumps(payload)
        payload = payload.encode("utf-8")
        response = self.predictor.invoke_model(body=payload, **self._params)
        response_body = json.loads(response.get("body").read())
        result = response_body.get(result_key)

        # fetch deeper result based on result_subkeys
        if result_subkeys is not None:
            for key in result_subkeys:
                if isinstance(result, list):
                    result = result[0].get(key)
                else:
                    result = result.get(key)
        return result  # noqa: E203

    @property
    def connected(self) -> bool:
        return self._connected
