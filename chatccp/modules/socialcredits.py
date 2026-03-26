from ..libraries.socialcredits import sclib

from discord.ext import commands
from discord import app_commands

import discord

class SocialCredits(commands.Cog, name="SocialCredits"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.score_tiers = [
            (1000, "Exemplary Citizen"),
            (999, "Model Citizen"),
            (749, "Active Contributor"),
            (499, "Average"),
            (249, "Needs Improvement"),
            (99, "At Risk"),
            (0, "Restricted Access"),
        ]

    @app_commands.command(
        name="socialcredits",
        description="Find your current social credit score."
    )
    async def socialcredits(self, interaction: discord.Interaction):
        (score, rating, is_supreme_leader) = sclib.get_user_rating(interaction.user.id)

        if is_supreme_leader:
            await interaction.response.send_message(f"# automated social credit scoring system :flag_cn:\nsupreme leader! :crown:\nmay you forever be blessed with prosperity and good fortune! :pray:\nyour score is `{score}` points, which is above the maximum rating tier. :star2:")

        await interaction.response.send_message(f"# automated social credit scoring system :flag_cn:\nyour current scoring: `{score}` points\nyour current rating: `{rating}`")

    @app_commands.command(
        name="creditleaders",
        description="See the top 10 users with the highest social credit scores."
    )
    async def creditleaders(self, interaction: discord.Interaction):
        # Fetch top 10 users with the highest social credit scores
        top_users = sclib.get_leaderboard(limit=10)

        # Format the leaderboard message
        leaderboard_message = "# social credit leaderboard :flag_cn::sparkles:\n\n"
        for rank, (user_id, score, rating, is_supreme_leader) in enumerate(top_users, start=1):
            user_mention = f"<@{user_id}>"
            supreme_leader_badge = " :crown:" if is_supreme_leader else ""
            leaderboard_message += f"{rank}. {user_mention} - `{score}` points - `{rating}`{supreme_leader_badge}\n"

        await interaction.response.send_message(leaderboard_message)

async def setup(Bot: commands.Bot):
    await Bot.add_cog(
        SocialCredits(Bot)
    )
