from src.chain.chain import ChainId
from src.concerns.moderation import ModerationPromptsOperationNames
from src.contracts.adapters.ai_api import AIApiClientInterface
from src.contracts.chain import ChainableServicesInterface
from src.core.deps.logger import with_logger
from src.exceptions.policies import ContentPolicyViolationException


class ModerationService:
    OPERATION_NAME = ModerationPromptsOperationNames.MODERATION.value

    def __init__(
        self,
        ai_api_client: AIApiClientInterface,
    ) -> None:
        self._ai_api_client = ai_api_client

    def is_violating_content_policy(self, text: str) -> bool:
        """
        Check if given text is safe to be returned to the user.

        Parameters
        ----------
        text : str
            Text to be checked.

        Returns
        -------
        bool
            False if text is safe, True otherwise.
        """

        # Pass chain id to AI API client
        self._ai_api_client.set_chain_id(self._chain_id)

        return self._ai_api_client.moderation(text, self.OPERATION_NAME)

    def set_chain_id(self, chain_id: ChainId) -> None:
        self._chain_id = chain_id


@with_logger()
class ModerationCheckOrFailService(ChainableServicesInterface):
    OPERATION_NAME = ModerationPromptsOperationNames.MODERATION.value

    def __init__(
        self,
        moderation_service: ModerationService,
    ) -> None:
        self._moderation_service = moderation_service

    def handle(self, input: str, **kwargs) -> str:
        """
        Check if given text is safe to be returned to the user.

        Parameters
        ----------
        input : str
            Text to be checked.

        Returns
        -------
        str
            Text if it is safe to be returned to the user.

        Raises
        ------
        ContentPolicyViolationException
        """

        # Pass chain id to moderation service
        self._moderation_service.set_chain_id(self._chain_id)
        self._logger.info(
            f"[Authoring] Executing Moderation prompt on {self._chain_id}"
        )

        # Check if input is violating content policy
        if self._moderation_service.is_violating_content_policy(input):
            raise ContentPolicyViolationException()

        return input

    def set_chain_id(self, chain_id: ChainId) -> None:
        self._chain_id = chain_id
