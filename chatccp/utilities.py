from .model import (
    MessageAttributes,
    ReplyChain
)

import discord
import re

def normalise(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

async def preprocess_message(message: discord.Message) -> str:
    # replace user mentions (and channel mentions) with their respective 
    # names, so that the model can understand them better
    content = normalise(message.content)

    for user in message.mentions:
        content = content.replace(f"<@{user.id}>", f"<@{user.id}> ({user.name})")

    for channel in message.channel_mentions:
        content = content.replace(f"<#{channel.id}>", f"<#{channel.id}> ({channel.name})")

    return f"<@{message.author.id}> ({message.author.name}): {content}"

async def get_reply_chain(
    self,
    message: discord.Message,
    max_depth: int = 5
) -> ReplyChain:
    reply_chain: list[discord.Message] = []
    depth = 0

    current_message = message

    while current_message.reference and current_message.reference.message_id and depth < max_depth:
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

        processed = await preprocess_message(referenced_message)
        reply_chain.append(processed)

        # keep walking up the chain using the actual message
        current_message = referenced_message
        depth += 1

    reply_chain.reverse()

    return ReplyChain(
        first_author=current_message.author,
        messages=reply_chain
    )

async def get_message_attributes(
    self,
    message: discord.Message,
    bot: discord.Client,
    max_depth: int = 5
) -> MessageAttributes:
    is_reply_to_bot = (
        message.reference and
        message.reference.resolved and
        message.reference.resolved.author == bot
    )

    reply_chain = await get_reply_chain(message, max_depth=max_depth) if is_reply_to_bot else ReplyChain(
        first_author=None,
        messages=[]
    )

    return MessageAttributes(
        has_trigger=any(trigger in normalise(message.content) for trigger in self.triggers),
        is_mentioned=self.bot.user.mentioned_in(message),
        is_reply_to_bot=is_reply_to_bot,
        reply_chain=reply_chain
    )
