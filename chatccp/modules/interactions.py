from ..inference import Inference
from ..utilities import (
    preprocess_message,
    normalise
)

from discord.ext import commands
from discord import app_commands

import logging
import discord
import re
import os

logger = logging.getLogger(__name__)

class Interactions(commands.Cog, name="Interactions"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.reply_chain_max_depth = int(os.getenv("REPLY_CHAIN_MAX_DEPTH", "4"))
        self.include_reply_chain = (os.getenv("INCLUDE_REPLY_CHAIN", "0").lower() == "1")

        self.inference = Inference()
        self.triggers = [
            "tiananmen",
            "tiananmen square",
            "tiananmen massacre",
            "tank man",
            "tankman",
            "1989 protests",
            "1989 protests in china",
            "1989 protests in tiananmen square",
            "1989 beijing protests",
            "beijing massacre",
            "june 4",
            "june 4th",
            "june fourth",
            "64 incident",
            "six four",
            "winnie the pooh",
            "winnie pooh",
            "pooh",
            "xi",
            "xi jinping",
            "xi jin ping",
            "president xi",
            "mao",
            "mao zedong",
            "mao ze dong",
            "mao leader",
            "mao zedong leader",
            "mao ze dong leader",
            "taiwan independence",
            "independent taiwan",
            "taiwan is a country",
            "free taiwan",
            "hong kong protests",
            "free hong kong",
            "hong kong democracy",
            "ccp",
            "chinese communist party",
            "social credits"
        ]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # let command handling own command messages
        # without invoking inference
        context = await self.bot.get_context(message)

        if context.valid:
            return

        has_trigger = any(trigger in normalise(message.content) for trigger in self.triggers)
        # TODO: Complete this

    async def collect_message_chain(
        self,
        original_message: discord.Message
    ) -> list[discord.Message]:
        if not self.include_reply_chain:
            return [original_message]

        message_chain: list[discord.Message] = [original_message]
        current_message = original_message
        current_depth = 0

        while (
            current_message.reference and
            current_message.reference.resolved and
            current_depth < self.reply_chain_max_depth
        ):
            referenced_message = current_message.reference.resolved

            # if discord.py didn't already resolve it to
            # a real Message, fetch it
            if not isinstance(referenced_message, discord.Message):
                try:
                    referenced_message = await current_message.channel.fetch_message(
                        current_message.reference.message_id
                    )
                except discord.NotFound:
                    break
                except discord.Forbidden:
                    break

            # append the real message to the chain
            message_chain.append(referenced_message)

            # keep walking up the chain using the actual message
            current_message = referenced_message
            depth += 1

        return message_chain.reverse()

    @app_commands.command(
        name="ask",
        description="Ask ChatCCP any question you want!"
    )
    @app_commands.describe(
        query="The question you want to ask ChatCCP."
    )
    async def ask(self, interaction: discord.Interaction, query: str):
        # collect the message chain
        message_chain = await self.collect_message_chain(interaction.message)

        # prepare the message list for inference
        messages = []

        for message in message_chain:
            messages.append({
                "role": "user" if message.author != self.bot.user else "assistant",
                "content": await preprocess_message(message)
            })

        # start the typing indicator
        # while we wait for inference
        # to complete
        await interaction.channel.typing()

        # send the query and filter
        # before replying to the user
        response = await self.inference.invoke(messages)

        response = re.sub(
            r"<think>.*?</think>", "",
            response,
            flags=re.DOTALL
        ).strip()

        await interaction.response.send_message(response)

async def setup(Bot: commands.Bot):
    await Bot.add_cog(
        Interactions(Bot)
    )
