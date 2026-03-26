from discord.ext import commands
from discord import app_commands

import discord

class Testing(commands.Cog, name="Testing"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="ping",
        description="check if the bot is responsive"
    )
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("pong!")

async def setup(Bot: commands.Bot):
    await Bot.add_cog(
        Testing(Bot)
    )
