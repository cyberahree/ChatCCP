from discord.ext import commands

class Auth(commands.Cog, name="Authentication"):
    pass

async def setup(Bot: commands.Bot):
    await Bot.add_cog(
        Auth(Bot)
    )
