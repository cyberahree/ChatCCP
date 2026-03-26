from ..inference import Inference
from ..utilities import normalise, preprocess_message_with_context

from discord.ext import commands
from discord import app_commands

import logging
import discord

logger = logging.getLogger(__name__)

class Interactions(commands.Cog, name="Interactions"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

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

    @app_commands.command(
        name="ask",
        description="Ask ChatCCP any question you want!"
    )
    @app_commands.guild_only()
    @app_commands.describe(
        message="The message you want to ask ChatCCP about."
    )
    async def ask(
        self,
        interaction: discord.Interaction,
        message: str
    ):
        # defer the response to give us more time to process the message
        # and invoke inference without hitting the interaction response timeout
        await interaction.response.defer(thinking=True)

        # process the message by resolving mentions to their display names
        processed_message = await preprocess_message_with_context(
            message, interaction.guild
        )

        # invoke inference with the processed message and send the response back to the user
        response = await self.inference.invoke(processed_message)

        # prepend the user's original message to the response for context
        reply = f"-# {interaction.user.mention}:\n{message}\n\n-# {self.bot.user.mention}:\n{response}"

        await interaction.followup.send(reply)

async def setup(Bot: commands.Bot):
    await Bot.add_cog(
        Interactions(Bot)
    )
