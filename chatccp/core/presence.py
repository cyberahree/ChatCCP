from discord.ext import (
    commands,
    tasks
)

import discord

class Presence(commands.Cog, name="Presence"):
    def __init__(self, bot):
        self.bot = bot
        self.possible_activities = []

        self.activities = [
            discord.Activity(
                type=discord.ActivityType.listening,
                name="the hard work within the factories"
            ),
            discord.Activity(
                type=discord.ActivityType.watching,
                name="the world burn"
            ),
            discord.Activity(
                type=discord.ActivityType.playing,
                name="with the lives of the people"
            ),
            discord.Activity(
                type=discord.ActivityType.competing,
                name="in the global domination tournament"
            )
        ]
    
    @tasks.loop(minutes=5)
    async def presence_task(self):
        if len(self.possible_activities) == 0:
            self.possible_activities = self.activities.copy()

        activity = self.possible_activities[0]
        self.possible_activities.append(self.possible_activities.pop(0))

        await self.bot.change_presence(activity=activity)
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.presence_task.start()

async def setup(bot: commands.Bot):
    await bot.add_cog(
        Presence(bot)
    )
