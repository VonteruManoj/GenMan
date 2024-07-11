import json

import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential

from src.chain.chain import ChainId
from src.contracts.adapters.ai_api import AIApiClientInterface
from src.core.deps.logger import with_logger
from src.exceptions.ai_api import AIApiResponseFormatException
from src.repositories.models.usage_log_repository import UsageLogRepository


@with_logger()
class OpenAIClient(AIApiClientInterface):
    def __init__(
        self,
        org_id: str,
        api_key: str,
        usage_log_repository: UsageLogRepository,
    ) -> None:
        self._client = openai
        self._client.organization = org_id
        self._client.api_key = api_key
        self._usage_log_repository = usage_log_repository
        self._logger.info("OpenAI API client initialized")

    @retry(
        reraise=True,
        wait=wait_random_exponential(min=1, max=20),
        stop=stop_after_attempt(3),
    )
    def completion(
        self,
        prompt: str,
        original_text: str,
        operation: str,
        configs: dict = {},
    ) -> str:
        args = configs | {"prompt": prompt}
        response = self._client.Completion.create(**args)
        self._logger.info(
            f"OpenAI API completion called with: {json.dumps(args)}"
        )

        try:
            return_value = response["choices"][0]["text"].strip()

            # Log usage
            self._usage_log_repository.create(
                operation=operation,
                prompt=json.dumps(prompt),
                input=json.dumps(original_text),
                response=json.dumps(response),
                output=json.dumps(return_value),
                chain_id=self._chain_id.id,
                chain_operation=self._chain_id.operation,
            )

            return return_value
        except (KeyError, IndexError):
            self._logger.warning(
                "OpenAI API completion response"
                f" without choices, prompt: {json.dumps(prompt)}"
            )

            raise AIApiResponseFormatException()

    @retry(
        reraise=True,
        wait=wait_random_exponential(min=1, max=20),
        stop=stop_after_attempt(3),
    )
    def chat_completion(
        self,
        messages: list[dict],
        original_text: str,
        operation: str,
        configs: dict = {},
    ) -> str:
        args = configs | {"messages": messages}
        response = self._client.ChatCompletion.create(**args)
        self._logger.info(
            f"OpenAI API chat completion called with: {json.dumps(args)}",
        )

        try:
            choice = response["choices"][0]["message"]["content"].strip()

            # Log usage
            self._usage_log_repository.create(
                operation=operation,
                prompt=json.dumps(messages),
                input=json.dumps(original_text),
                response=json.dumps(response),
                output=json.dumps(choice),
                chain_id=self._chain_id.id,
                chain_operation=self._chain_id.operation,
            )

            return choice
        except (KeyError, IndexError):
            self._logger.warning(
                "OpenAI API chat completion response"
                f" without choices, messages: {json.dumps(messages)}"
            )

            raise AIApiResponseFormatException()

    @retry(
        reraise=True,
        wait=wait_random_exponential(min=1, max=20),
        stop=stop_after_attempt(3),
    )
    def moderation(self, input: str, operation: str) -> bool:
        """
        Moderation is done by the OpenAI API by using the ChatCompletion
        endpoint. The response contains a "flagged" field that indicates
        if the input is safe or not.

        Parameters
        ----------
        input : str
            Input to be moderated
        operation : str
            Operation name to be used in the logs

        Returns
        -------
        bool
            False if the input is safe, True otherwise
        """
        response = self._client.Moderation.create(input)
        args = {"input": input, "operation": operation}
        self._logger.info(
            f"OpenAI API moderation called with: {json.dumps(args)}"
        )

        try:
            flagged = response["results"][0]["flagged"]

            # Log usage
            self._usage_log_repository.create(
                operation=operation,
                prompt=json.dumps(input),
                input=json.dumps(input),
                response=json.dumps(response),
                output=json.dumps(flagged),
                chain_id=self._chain_id.id,
                chain_operation=self._chain_id.operation,
            )

            return flagged
        except KeyError:
            self._logger.warning(
                "OpenAI API invalid moderation response,"
                f" input: {json.dumps(input)}"
            )

            raise AIApiResponseFormatException()

    def set_chain_id(self, chain_id: ChainId) -> None:
        self._chain_id = chain_id


@with_logger()
class FakeOpenAIClient(AIApiClientInterface):
    def __init__(self, usage_log_repository: UsageLogRepository) -> None:
        self._usage_log_repository = usage_log_repository
        self._logger.info("[FAKE] OpenAI API client initialized")

    def completion(
        self,
        prompt: str,
        original_text: str,
        operation: str,
        configs: dict = {},
    ) -> str:
        return_value = f"This is a completion fake response, prompt: {prompt}"

        args = configs | {"prompt": prompt}
        self._logger.info(
            f"[FAKE] OpenAI API completion called with: {json.dumps(args)}",
        )

        # Log usage
        self._usage_log_repository.create(
            operation=operation,
            prompt=json.dumps("Local call"),
            input=json.dumps(original_text),
            response=json.dumps("Local call"),
            output=json.dumps(return_value),
            chain_id=self._chain_id.id,
            chain_operation=self._chain_id.operation,
        )

        return return_value

    def chat_completion(
        self,
        messages: list[dict],
        original_text: str,
        operation: str,
        configs: dict = {},
    ) -> str:
        choice = (
            "This is a chat completion fake response,"
            f" messages: {json.dumps(messages)}"
        )

        args = configs | {"messages": messages}
        self._logger.info(
            "[FAKE] OpenAI API chat completion"
            f" called with: {json.dumps(args)}",
        )

        # Log usage
        self._usage_log_repository.create(
            operation=operation,
            prompt=json.dumps("Local call"),
            input=json.dumps(original_text),
            response=json.dumps("Local call"),
            output=json.dumps(choice),
            chain_id=self._chain_id.id,
            chain_operation=self._chain_id.operation,
        )

        return choice

    def moderation(
        self,
        input: str,
        operation: str,
    ) -> bool:
        self._logger.info(
            f"[FAKE] OpenAI API moderation called with: {json.dumps(input)}",
        )

        # Log usage
        self._usage_log_repository.create(
            operation=operation,
            prompt=json.dumps("Local call"),
            input=json.dumps(input),
            response=json.dumps("Local call"),
            output=json.dumps(False),
            chain_id=self._chain_id.id,
            chain_operation=self._chain_id.operation,
        )

        return False

    def set_chain_id(self, chain_id: ChainId) -> None:
        self._chain_id = chain_id
