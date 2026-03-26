from dataclasses import dataclass

import discord

@dataclass
class ReplyChain:
    first_author: discord.User
    messages: list[str]

@dataclass
class MessageAttributes:
    has_trigger: bool
    is_mentioned: bool
    is_reply_to_bot: bool
    reply_chain: ReplyChain = None