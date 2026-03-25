from discord.ext import commands

class Module(commands.Cog, name="Module"):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await ctx.bot.is_owner(ctx.author)

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("you are not allowed to use this command.")
            return

        raise error

    def extension_to_path(self, extension_name: str):
        return self.bot.ROOT / (extension_name.replace(".", "/") + ".py")

    def is_local_extension(self, extension_name: str) -> bool:
        if extension_name not in self.bot.extensions:
            return False

        return self.extension_to_path(extension_name).is_file()

    def normalize_module_input(self, module: str) -> str:
        requested = module.strip()
        requested = requested.removesuffix(".py")
        requested = requested.replace("\\", ".").replace("/", ".")
        requested = requested.removeprefix("./").removeprefix(".")
        return requested

    async def resolve_reloadable_module(self, module: str) -> str:
        requested = self.normalize_module_input(module)

        if len(requested) == 0:
            raise ValueError("please specify a module to reload")

        loaded_modules = sorted(
            extension_name
            for extension_name in self.bot.extensions.keys()
            if extension_name.startswith("modules.") and self.is_local_extension(extension_name)
        )

        if len(loaded_modules) == 0:
            raise ValueError("no reloadable modules are currently loaded")

        # 1) Exact extension name wins immediately.
        if requested in loaded_modules:
            return requested

        # 2) Exact shorthand (modules.<name>).
        prefixed = f"modules.{requested}"
        if prefixed in loaded_modules:
            return prefixed

        # 3) Exact short-name match among loaded module extensions.
        short_exact = [
            extension_name
            for extension_name in loaded_modules
            if extension_name.removeprefix("modules.") == requested
        ]
        if len(short_exact) == 1:
            return short_exact[0]

        # 4) Prefix shorthand (e.g. inter -> modules.interactions).
        prefix_matches = [
            extension_name
            for extension_name in loaded_modules
            if extension_name.removeprefix("modules.").startswith(requested)
        ]

        if len(prefix_matches) == 1:
            return prefix_matches[0]

        if len(prefix_matches) > 1:
            options = ", ".join(prefix_matches)
            raise ValueError(f"ambiguous module '{module}'. use one of: {options}")

        available = ", ".join(name.removeprefix("modules.") for name in loaded_modules)
        raise ValueError(f"{module} is not reloadable. available: {available}")

    async def reload_extension_module(self, module: str) -> str:
        resolved = await self.resolve_reloadable_module(module)
        await self.bot.reload_extension(resolved)
        return resolved

    @commands.command(
        name="listmod",
        aliases=["listmodules", "modules", "mods"]
    )
    async def list_modules(self, ctx: commands.Context):
        """Lists all loaded modules."""
        modules = []

        for file in (self.bot.ROOT / "modules").glob("*.py"):
            if file.name == "__init__.py":
                continue

            modules.append(file.stem)

        if len(modules) == 0:
            await ctx.send("no modules found :(")
        else:
            await ctx.send("**certified modules :flag_cn:**\n```" + "\n".join(modules) + "```")

    @commands.command(
        name="reloadmod",
        aliases=["reloadmodule", "reloadmods", "reloadmodules"]
    )
    async def reload_module(self, ctx: commands.Context, module_name: str | None = None):
        """Reloads a specified module, (or alternatively a provided shorthand for that module, if not ambiguous)."""
        if not module_name:
            await ctx.send("please specify a module to reload.")
            return

        try:
            resolved = await self.reload_extension_module(module_name)
            await ctx.send(f"reloaded module `{resolved}` successfully.")
        except Exception as e:
            await ctx.send(f"failed to reload module `{module_name}`: {e}")

async def setup(Bot: commands.Bot):
    await Bot.add_cog(
        Module(Bot)
    )
