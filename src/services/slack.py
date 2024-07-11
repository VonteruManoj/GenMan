from slack_sdk import WebClient

from src.contracts.services.slack import SlackServiceInterface
from src.core.deps.logger import with_logger


def prepare_function_log_message(name: str, input: str, output: str) -> str:
    str = (
        "*Function:* %s\n"
        "*Input:* %s\n"
        "*Output:* %s\n"
        % (
            name,
            input,
            output,
        )
    )

    return str


@with_logger()
class SlackService(SlackServiceInterface):
    def __init__(
        self,
        channel_id: str,
        token: str,
    ) -> None:
        self.channel_id = channel_id
        self.client = WebClient(token=token)

    def send_message(self, text: str) -> None:
        try:
            self.client.chat_postMessage(channel=self.channel_id, text=text)
            self._logger.info(
                "Slack message sent to channel: %s", self.channel_id
            )
        except Exception as e:
            self._logger.warning(
                "Error [%s] sending Slack message to channel: %s",
                e,
                self.channel_id,
            )

    def send_function_log_message(
        self, name: str, input: str, output: str
    ) -> None:
        self.send_message(prepare_function_log_message(name, input, output))


@with_logger()
class FakeSlackService(SlackServiceInterface):
    def send_message(self, text: str) -> None:
        self._logger.info('[FAKE] Slack message "%s" sent.', text)

    def send_function_log_message(
        self, name: str, input: str, output: str
    ) -> None:
        self.send_message(prepare_function_log_message(name, input, output))
