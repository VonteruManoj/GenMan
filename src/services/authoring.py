from abc import abstractmethod

from src.builders.prompts import (
    ChangeTonePromptBuilder,
    ExpandWritingBuilder,
    FixGrammarPromptBuilder,
    ImproveWritingPromptBuilder,
    ReduceReadingComplexityBuilder,
    ReduceReadingTimeBuilder,
    SummarizeIntoStepsPromptBuilder,
    SummarizePromptBuilder,
    TranslatePromptBuilder,
)
from src.chain.chain import ChainId
from src.concerns.authoring import AuthoringPromptsOperationNames
from src.contracts.adapters.ai_api import AIApiClientInterface
from src.contracts.chain import ChainableServicesInterface
from src.contracts.repositories.assets import AssetsRepositoryInterface
from src.contracts.services.slack import SlackServiceInterface
from src.core.deps.logger import with_logger
from src.schemas.assets.prompts import PromptTemplates


@with_logger()
class AuthoringService(ChainableServicesInterface):
    OPERATION_NAME = None

    def __init__(
        self,
        ai_api_client: AIApiClientInterface,
        assets_repo: AssetsRepositoryInterface,
        templates_filename: str,
        slack_service: SlackServiceInterface,
    ) -> None:
        self._ai_api_client = ai_api_client
        self._assets_repo = assets_repo
        self.load_template_configs(templates_filename)
        self._slack_service = slack_service
        self._init_prompt_builder()
        self._chain_id = ChainId()

    def load_template_configs(self, filename):
        try:
            self._logger.debug(
                f"[Authoring] Loading template configs: {filename}"
            )
            templates = self._assets_repo.get_json_asset(filename)
            self._templates = PromptTemplates.parse_obj(templates)
            self._logger.debug(
                f"[Authoring] Loaded template configs: {filename}"
            )
        except Exception as e:
            raise e

    @property
    def templates(self) -> PromptTemplates:
        return self._templates

    @abstractmethod
    def handle(self, input: str, **kwargs) -> str:
        """Handle the input"""

    @abstractmethod
    def _init_prompt_builder(self) -> None:
        """Initialize the prompt builder"""

    def set_chain_id(self, chain_id: ChainId) -> None:
        self._chain_id = chain_id


@with_logger()
class FixGrammarAuthoringService(AuthoringService):
    OPERATION_NAME = AuthoringPromptsOperationNames.FIX_GRAMMAR.value

    def _init_prompt_builder(self) -> None:
        self._prompt_builder = FixGrammarPromptBuilder()

    def handle(self, input: str, **kwargs) -> str:
        self._logger.info("[Authoring] Executing Fix Grammar prompt...")

        # Get template
        template = self.templates.FixGrammar

        # Build prompt
        self._prompt_builder.template = template.prompt  # todo
        prompt = self._prompt_builder.build(input)

        # Pass chain id to AI API client
        self._ai_api_client.set_chain_id(self._chain_id)

        # Get choice
        choice = self._ai_api_client.completion(
            prompt,
            input,
            self.OPERATION_NAME,
            template.get_configs(),
        )

        self._logger.info("[Authoring] Executed Fix Grammar prompt")

        # Send Slack log message
        self._slack_service.send_function_log_message(
            "Fix Grammar", input, choice
        )

        return choice


@with_logger()
class SummarizeService(AuthoringService):
    OPERATION_NAME = AuthoringPromptsOperationNames.SUMMARIZE.value

    def _init_prompt_builder(self) -> None:
        self._prompt_builder = SummarizePromptBuilder()

    def handle(self, input: str, **kwargs) -> str:
        self._logger.info("[Authoring] Executing Summarize prompt...")
        # Get template
        template = self.templates.Summarize

        # Build prompt
        self._prompt_builder.template = template
        prompt = self._prompt_builder.build(input)

        # Pass chain id to AI API client
        self._ai_api_client.set_chain_id(self._chain_id)

        # Get choice
        choice = self._ai_api_client.chat_completion(
            prompt, input, self.OPERATION_NAME, template.get_configs()
        )

        self._logger.info("[Authoring] Executed Summarize prompt...")

        # Send Slack log message
        self._slack_service.send_function_log_message(
            "Summarize", input, choice
        )

        return choice


@with_logger()
class SummarizeIntoStepsService(AuthoringService):
    OPERATION_NAME = AuthoringPromptsOperationNames.SUMMARIZE_INTO_STEPS.value

    def _init_prompt_builder(self) -> None:
        self._prompt_builder = SummarizeIntoStepsPromptBuilder()

    def handle(self, input: str, **kwargs) -> str:
        self._logger.info(
            "[Authoring] Executing Summarize Into Steps prompt..."
        )

        # Get template
        template = self.templates.SummarizeIntoSteps

        # Build prompt
        self._prompt_builder.template = template
        prompt = self._prompt_builder.build(input)

        # Pass chain id to AI API client
        self._ai_api_client.set_chain_id(self._chain_id)

        # Get choice
        choice = self._ai_api_client.chat_completion(
            prompt, input, self.OPERATION_NAME, template.get_configs()
        )

        self._logger.info(
            "[Authoring] Executed Summarize Into Steps prompt..."
        )

        # Send Slack log message
        self._slack_service.send_function_log_message(
            "Summarize Into Steps", input, choice
        )

        return choice


@with_logger()
class ChangeToneService(AuthoringService):
    OPERATION_NAME = AuthoringPromptsOperationNames.CHANGE_TONE.value

    def _init_prompt_builder(self) -> None:
        self._prompt_builder = ChangeTonePromptBuilder()

    def handle(self, input: str, tone: str, **kwargs) -> str:
        self._logger.info(
            f"[Authoring] Executing Change Tone [{tone}] prompt..."
        )

        # Get template
        template = self.templates.ChangeTone

        # Build prompt
        self._prompt_builder.template = template
        prompt = self._prompt_builder.build(input, tone)

        # Pass chain id to AI API client
        self._ai_api_client.set_chain_id(self._chain_id)

        # Get choice
        choice = self._ai_api_client.chat_completion(
            prompt, input, self.OPERATION_NAME, template.get_configs()
        )

        self._logger.info(
            f"[Authoring] Executed Change Tone [{tone}] prompt..."
        )

        # Send Slack log message
        self._slack_service.send_function_log_message(
            f"Change Tone [{tone}]", input, choice
        )

        return choice


@with_logger()
class TranslateService(AuthoringService):
    OPERATION_NAME = AuthoringPromptsOperationNames.TRANSLATE.value

    def _init_prompt_builder(self) -> None:
        self._prompt_builder = TranslatePromptBuilder()

    def handle(self, input: str, language: str, **kwargs) -> str:
        self._logger.info(
            f"[Authoring] Executing Translate [to: {language}] prompt..."
        )

        # Get template
        template = self.templates.Translate

        # Build prompt
        self._prompt_builder.template = template
        prompt = self._prompt_builder.build(input, language)

        # Pass chain id to AI API client
        self._ai_api_client.set_chain_id(self._chain_id)

        # Get choice
        choice = self._ai_api_client.chat_completion(
            prompt, input, self.OPERATION_NAME, template.get_configs()
        )

        self._logger.info(
            f"[Authoring] Executed Translate [to: {language}] prompt..."
        )

        # Send Slack log message
        self._slack_service.send_function_log_message(
            f"Translate [to: {language}]", input, choice
        )

        return choice


@with_logger()
class ImproveWritingService(AuthoringService):
    OPERATION_NAME = AuthoringPromptsOperationNames.IMPROVE_WRITING.value

    def _init_prompt_builder(self) -> None:
        self._prompt_builder = ImproveWritingPromptBuilder()

    def handle(self, input: str, **kwargs) -> str:
        self._logger.info("[Authoring] Executing Improve Writing prompt...")

        # Get template
        template = self.templates.ImproveWriting

        # Build prompt
        self._prompt_builder.template = template
        prompt = self._prompt_builder.build(input)

        # Pass chain id to AI API client
        self._ai_api_client.set_chain_id(self._chain_id)

        # Get choice
        choice = self._ai_api_client.chat_completion(
            prompt, input, self.OPERATION_NAME, template.get_configs()
        )

        self._logger.info("[Authoring] Executed Improve Writing prompt...")

        # Send Slack log message
        self._slack_service.send_function_log_message(
            "Improve Writing", input, choice
        )

        return choice


@with_logger()
class ReduceReadingComplexityService(AuthoringService):
    OPERATION_NAME = (
        AuthoringPromptsOperationNames.REDUCE_READING_COMPLEXITY.value
    )

    def _init_prompt_builder(self) -> None:
        self._prompt_builder = ReduceReadingComplexityBuilder()

    def handle(self, input: str, **kwargs) -> str:
        self._logger.info(
            "[Authoring] Executing Reduce Reading Complexity prompt..."
        )

        # Get template
        template = self.templates.ReduceReadingComplexity

        # Build prompt
        self._prompt_builder.template = template
        prompt = self._prompt_builder.build(input)

        # Pass chain id to AI API client
        self._ai_api_client.set_chain_id(self._chain_id)

        # Get choice
        choice = self._ai_api_client.chat_completion(
            prompt, input, self.OPERATION_NAME, template.get_configs()
        )

        self._logger.info(
            "[Authoring] Executed Reduce Reading Complexity prompt..."
        )

        # Send Slack log message
        self._slack_service.send_function_log_message(
            "Reduce Reading Complexity", input, choice
        )

        return choice


@with_logger()
class ReduceReadingTimeService(AuthoringService):
    OPERATION_NAME = AuthoringPromptsOperationNames.REDUCE_READING_TIME.value

    def _init_prompt_builder(self) -> None:
        self._prompt_builder = ReduceReadingTimeBuilder()

    def handle(self, input: str, **kwargs) -> str:
        self._logger.info(
            "[Authoring] Executing Reduce Reading Time prompt..."
        )

        # Get template
        template = self.templates.ReduceReadingTime

        # Build prompt
        self._prompt_builder.template = template
        prompt = self._prompt_builder.build(input)

        # Pass chain id to AI API client
        self._ai_api_client.set_chain_id(self._chain_id)

        # Get choice
        choice = self._ai_api_client.chat_completion(
            prompt, input, self.OPERATION_NAME, template.get_configs()
        )

        self._logger.info("[Authoring] Executed Reduce Reading Time prompt...")

        # Send Slack log message
        self._slack_service.send_function_log_message(
            "Reduce Reading Time", input, choice
        )

        return choice


@with_logger()
class ExpandWritingService(AuthoringService):
    OPERATION_NAME = AuthoringPromptsOperationNames.EXPAND_WRITING.value

    def _init_prompt_builder(self) -> None:
        self._prompt_builder = ExpandWritingBuilder()

    def handle(self, input: str, **kwargs) -> str:
        self._logger.info("[Authoring] Executing Expand Writing prompt...")

        # Get template
        template = self.templates.ExpandWriting

        # Build prompt
        self._prompt_builder.template = template
        prompt = self._prompt_builder.build(input)

        # Pass chain id to AI API client
        self._ai_api_client.set_chain_id(self._chain_id)

        # Get choice
        choice = self._ai_api_client.chat_completion(
            prompt, input, self.OPERATION_NAME, template.get_configs()
        )

        self._logger.info("[Authoring] Executed Expand Writing prompt")

        # Send Slack log message
        self._slack_service.send_function_log_message(
            "Expand Writing", input, choice
        )

        return choice
