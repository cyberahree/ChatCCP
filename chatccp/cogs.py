from discord.ext import commands

from pathlib import Path

import logging

FILE = Path(__file__).resolve()
ROOT = FILE.parent

logger = logging.getLogger(__name__)

class Modules:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self._modules: list[str] = []
        self._core: list[str] = []
        self._loaded = False

        self._load_modules()

    @property
    def modules(self):
        return self._modules

    @property
    def core(self):
        return self._core

    def _load_modules(self):
        self._modules.clear()
        self._core.clear()

        for file in (ROOT / "modules").glob("*.py"):
            if file.name == "__init__.py":
                continue

            module_name = self._module_from_directory(file)
            self._modules.append(module_name)

        for file in (ROOT / "core").glob("*.py"):
            if file.name == "__init__.py":
                continue

            module_name = self._module_from_directory(file)
            self._core.append(module_name)

    def _module_from_directory(self, module: Path):
        if not module.is_file():
            raise ValueError(f"{module} is not a file")
        
        if not module.suffix == ".py":
            raise ValueError(f"{module} is not a Python file")
        
        # calculate relative to the parent of the chatccp package to get full import path
        module_path = module.relative_to(ROOT.parent)
        module_name = module_path.with_suffix("").as_posix().replace("/", ".")

        return module_name
    
    async def init_modules(self):
        if self._loaded:
            raise RuntimeError("Modules have already been loaded")

        self._loaded = True

        for module in self._core:
            logger.info(f"Loading core module: {module}")
            await self.bot.load_extension(module)

        for module in self._modules:
            logger.info(f"Loading module: {module}")
            await self.bot.load_extension(module)

    def get_modules_by_name(self, name: str) -> list[str]:
        name = name.strip()

        if len(name) == 0:
            raise ValueError("Module name cannot be empty")

        # check for partial matches
        # or if there's an exact match among loaded modules
        matches = []

        for module in self.modules:
            if module == name:
                return [module]
            elif module.endswith(name):
                matches.append(module)

        return matches

    async def reload_module(self, module: str):
        matched_modules = self.get_modules_by_name(module)

        if len(matched_modules) != 1:
            raise ValueError(f"Module name '{module}' is ambiguous. Matches: {matched_modules}")
        
        module_to_reload = matched_modules[0]
        await self.bot.reload_extension(module_to_reload)

    async def reload_modules(self, modules: list[str]):
        for module in modules:
            await self.reload_module(module)
