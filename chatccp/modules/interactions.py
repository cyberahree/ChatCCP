from inference import (
    Inference,
    normalize
)

from dataclasses import dataclass
from discord.ext import commands

import logging
import discord
import re
import os

logger = logging.getLogger(__name__)

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

class Interactions(commands.Cog, name="Interactions"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.reply_chain_max_depth = int(os.getenv("REPLY_CHAIN_MAX_DEPTH", 4))
        self.include_reply_chain = (os.getenv("INCLUDE_REPLY_CHAIN", "0").lower() == "1")

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

    async def get_reply_chain(self, message: discord.Message) -> ReplyChain:
        reply_chain: list[discord.Message] = []
        depth = 0

        current_message = message

        if not self.include_reply_chain:
            return ReplyChain(
                first_author=current_message.author,
                messages=[]
            )

        while current_message.reference and current_message.reference.message_id and depth < self.reply_chain_max_depth:
            referenced_message = current_message.reference.resolved

            # if discord.py didn't already resolve it to
            # a real Message, fetch it
            if not isinstance(referenced_message, discord.Message):
                try:
                    referenced_message = await current_message.channel.fetch_message(
                        current_message.reference.message_id
                    )
                except discord.NotFound:
                    break
                except discord.Forbidden:
                    break

            processed = await self.preprocess_message(referenced_message)
            reply_chain.append(processed)

            # keep walking up the chain using the actual message
            current_message = referenced_message
            depth += 1

        reply_chain.reverse()

        return ReplyChain(
            first_author=current_message.author,
            messages=reply_chain
        )

    async def get_message_attributes(self, message: discord.Message) -> MessageAttributes:
        is_reply_to_bot = (
            message.reference and
            message.reference.resolved and
            message.reference.resolved.author == self.bot.user
        )

        reply_chain = await self.get_reply_chain(message) if is_reply_to_bot else []

        return MessageAttributes(
            has_trigger=any(trigger in normalize(message.content) for trigger in self.triggers),
            is_mentioned=self.bot.user.mentioned_in(message),
            is_reply_to_bot=is_reply_to_bot,
            reply_chain=reply_chain
        )

    async def preprocess_message(self, message: discord.Message) -> str:
        # replace user mentions (and channel mentions) with their respective 
        # names, so that the model can understand them better
        content = normalize(message.content)

        for user in message.mentions:
            content = content.replace(f"<@{user.id}>", f"<@{user.id}> ({user.name})")

        for channel in message.channel_mentions:
            content = content.replace(f"<#{channel.id}>", f"<#{channel.id}> ({channel.name})")

        return f"<@{message.author.id}> ({message.author.name}): {content}"

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # let command handling own command messages
        # without invoking inference
        context = await self.bot.get_context(message)

        if context.valid:
            return

        # collect message attributes, such as
        # whether it contains triggers,
        # mentions the bot,
        # or is a reply to the bot        
        message_attributes = await self.get_message_attributes(message)
        should_respond = (
            message_attributes.has_trigger or
            message_attributes.is_mentioned or
            message_attributes.is_reply_to_bot
        )

        # if none of the conditions for responding are met, ignore the message
        if not should_respond:
            return

        # build a timeline, starting with the reply chain if the message is a reply to the bot
        # otherwise just use the current message as the timeline
        # this is an overt use of tokens, increasing context
        first_author = message.author
        timeline = []

        try:
            if message_attributes.is_reply_to_bot and self.include_reply_chain:
                first_author = message_attributes.reply_chain.first_author
                timeline = message_attributes.reply_chain.messages
        except Exception as e:
            # if anything goes wrong with fetching the reply chain, just ignore it and use the current message
            logger.error(f"Error fetching reply chain: {e}")

        timeline.append(await self.preprocess_message(message))

        # restructure so it works with the api
        messages = []
        is_user = (first_author != self.bot.user)
        
        for timeline_message in timeline:
            messages.append({
                "role": "user" if is_user else "assistant",
                "content": timeline_message
            })

            is_user = not is_user

        async with message.channel.typing():
            response = await self.inference.invoke(messages)
            response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()

        await message.reply(response)

async def setup(Bot: commands.Bot):
    await Bot.add_cog(
        Interactions(Bot)
    )
