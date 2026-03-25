from .logger import setup_logging

from discord.ext import commands

from pathlib import Path

import logging
import discord
import sys
import os

FILE = Path(__file__).resolve()
DIR = FILE.parent

logger = logging.getLogger(__name__)

class ChatCCP(commands.Bot):
    def __init__(self):
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

    def module_from_directory(self, module: Path, directory: Path = DIR):
        if not module.is_file():
            raise ValueError(f"{module} is not a file")
        
        if not module.suffix == ".py":
            raise ValueError(f"{module} is not a Python file")
        
        # get the module name from the file path
        module_path = module.relative_to(directory)
        module_name = module_path.with_suffix("").as_posix().replace("/", ".")

        return module_name

    async def load_cog(self, cog: Path):
        module = self.module_from_directory(cog)
        await self.load_extension(module)

    async def load_cogs(self, directory: Path, graceful: bool = False):
        for file in directory.glob("*.py"):
            if file.name == "__init__.py":
                continue

            # gracefully load cogs,
            # if graceful is True,
            # otherwise raise exceptions
            try:
                await self.load_cog(file)
            except Exception as e:
                if not graceful:
                    raise e
                else:
                    logger.error(f"Failed to load {file}: {e}")

    async def setup_hook(self):
        await self.load_cogs(
            DIR / "core"
        )

        await self.load_cogs(
            DIR / "modules",
            graceful=True
        )

        await super().setup_hook()

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")

    def run(self):
        setup_logging()
        token = os.getenv("DISCORD_TOKEN", "")

        if len(token) == 0:
            logger.error("DISCORD_TOKEN environment variable is not set")
            sys.exit()

        super().run(token)

if __name__ == "__main__":
    pass
