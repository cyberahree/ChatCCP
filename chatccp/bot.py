from .logger import setup_logging
from .cogs import Modules

from discord.ext import commands

import logging
import discord
import sys
import os

logger = logging.getLogger(__name__)

class ChatCCP(commands.Bot):
    def __init__(self):
        self.MODULES = Modules(self)

        self.APPLICATION_ID = int(os.getenv("DISCORD_APPLICATION_ID", 0))

        if self.APPLICATION_ID == 0:
            logger.error("DISCORD_APPLICATION_ID environment variable is not set or invalid")
            sys.exit()

        super().__init__(
            command_prefix=commands.when_mentioned_or("chatccp "),
            intents=discord.Intents.all(),
            application_id=self.APPLICATION_ID,
            help_command=None
        )

    async def setup_hook(self):
        await self.MODULES.init_modules()

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        # ignore unknown commands
        # so normal chat messages do not spam errors
        if isinstance(error, commands.CommandNotFound):
            return

        await super().on_command_error(ctx, error)

    def run(self):
        setup_logging()
        token = os.getenv("DISCORD_TOKEN", "")

        if len(token) == 0:
            logger.error("DISCORD_TOKEN environment variable is not set")
            sys.exit()

        super().run(token)
