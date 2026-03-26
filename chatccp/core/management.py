from discord.ext import commands

class Management(commands.Cog, name="Management"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await ctx.bot.is_owner(ctx.author)

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply("you are not allowed to use this command. 3:<")
            return

        raise error
    
    @commands.command(
        name="listcmds",
        aliases=["cmds", "commands"]
    )
    async def list_commands(self, ctx: commands.Context):
        if ctx.guild is None:
            await ctx.reply("this command can only be used in a server")
            return

        tree_commands = self.bot.tree.get_commands()

        if len(tree_commands) == 0:
            await ctx.reply("no commands found :(")
            return
        
        listed_commands = "\n".join(f"- `{command.name}`" for command in tree_commands)
        await ctx.reply(f"**certified commands :flag_cn:**\n{listed_commands}")
    
    @commands.command(
        name="treesync"
    )
    async def tree_sync(self, ctx: commands.Context):
        if ctx.guild is None:
            await ctx.reply("this command can only be used in a server")
            return

        # clear guild-level shadow copies so command names do not duplicate in this server
        self.bot.tree.clear_commands(guild=ctx.guild)
        await self.bot.tree.sync(guild=ctx.guild)

        # sync global commands; Discord may take time to propagate global updates
        synced_commands = await self.bot.tree.sync()
        listed = "\n".join(f"- `{command.name}`" for command in synced_commands)
        
        await ctx.reply(f"command tree synced successfully for guild `{ctx.guild.name}`.\nsynced global: {len(synced_commands)} command(s)\n{listed}")

    @commands.command(
        name="listmods",
        aliases=["listmodules", "modules"]
    )
    async def list_modules(self, ctx: commands.Context):
        modules = self.bot.CogsManager.modules

        if len(modules) == 0:
            await ctx.reply("no modules found :(")
            return

        cleaned_modules = [module.strip() for module in modules]
        module_lines = "\n".join(f"- `{module}`" for module in cleaned_modules)

        await ctx.reply(f"**certified modules :flag_cn:**\n{module_lines}",)

    @commands.command(
        name="reloadmod",
        aliases=["reloadmodule", "reloadmods", "reload"]
    )
    async def reload_module(self, ctx: commands.Context, module_name: str | None = None):
        if not module_name:
            await ctx.reply("please specify a module to reload")
            return

        try:
            real_module_name = await self.bot.CogsManager.reload_module(module_name)

            await ctx.reply(f"reloaded module `{real_module_name}` successfully")
        except ValueError as e:
            await ctx.reply(f"failed to reload module `{module_name}`: {e}")
        except Exception as e:
            await ctx.reply(f"failed to reload module `{module_name}`: {e}")

async def setup(Bot: commands.Bot):
    await Bot.add_cog(
        Management(Bot)
    )
