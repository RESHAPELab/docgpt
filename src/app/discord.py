from logging import getLogger
from typing import Any

import discord
from discord.flags import Intents

from src.domain.port.assistent import AssistentPort


class DiscordClient(discord.Client):
    _logger = getLogger(__name__)

    def __init__(
        self,
        *,
        assistent: AssistentPort,
        intents: Intents,
        **options: Any,
    ) -> None:
        super().__init__(intents=intents, **options)
        self._assistent = assistent

    async def on_ready(self) -> None:
        if self.user is None:
            raise Exception("User not logged")

        self._logger.info(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user:
            return
        if self.user not in message.mentions:
            return

        response = self._assistent.prompt(message.content)
        await message.channel.send(response, mention_author=True)
