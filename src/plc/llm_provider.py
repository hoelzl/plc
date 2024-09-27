from typing import Protocol

from plc.message import Message
from plc.model import Model


class LlmProvider(Protocol):
    async def send_message(self, messages: list[Message], model: Model) -> str: ...
