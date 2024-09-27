import json
import os

import aiohttp
import attrs
from attrs import define

from plc.message import Message
from plc.model import Model

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


@define
class OpenRouterProvider:
    api_key: str = OPENROUTER_API_KEY
    api_url: str = OPENROUTER_API_URL

    async def send_message(self, messages: list[Message], model: Model) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = json.dumps(
            {
                "model": model.id,
                "messages": [attrs.asdict(m) for m in messages],  # noqa
            }
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.api_url, headers=headers, data=data
            ) as response:
                if response.status == 200:
                    response_json = await response.json()
                    return response_json["choices"][0]["message"]["content"]
                else:
                    response_text = await response.text()
                    raise RuntimeError(f"Failed to convert chunk: {response_text}")
