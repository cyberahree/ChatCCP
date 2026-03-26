from discord.ext import commands

import discord

class Management(commands.Cog, name="Management"):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await ctx.bot.is_owner(ctx.author)

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("you are not allowed to use this command. 3:<")
            return

        raise error
    
    @commands.command(
        name="treesync",
        aliases=["ts", "sync"]
    )
    async def tree_sync(self, ctx: commands.Context):
        # sync the command tree to update slash commands
        await self.bot.tree.sync(
            guild=discord.Object(id=ctx.guild.id)
        )

        await ctx.send(f"command tree synced successfully for guild `{ctx.guild.name}`.")

    @commands.command(
        name="listmod",
        aliases=["listmodules", "modules", "mods"]
    )
    async def list_modules(self, ctx: commands.Context):
        modules = self.bot.MODULES.modules

        if len(modules) == 0:
            await ctx.send("no modules found :(")
        else:
            await ctx.send("**certified modules :flag_cn:**\n```" + "\n".join(modules) + "```")

    @commands.command(
        name="reloadmod",
        aliases=["reloadmodule", "reloadmods", "reloadmodules"]
    )
    async def reload_module(self, ctx: commands.Context, module_name: str | None = None):
        if not module_name:
            await ctx.send("please specify a module to reload.")
            return

        try:
            await self.bot.MODULES.reload_module(module_name)
            await ctx.send(f"reloaded module `{module_name}` successfully.")
        except ValueError as e:
            await ctx.send(f"failed to reload module `{module_name}`: {e}")
        except Exception as e:
            await ctx.send(f"failed to reload module `{module_name}`: {e}")

async def setup(Bot: commands.Bot):
    await Bot.add_cog(
        Management(Bot)
    )
