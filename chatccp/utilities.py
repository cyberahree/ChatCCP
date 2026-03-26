import discord
import re

CHANNEL_MATCH = re.compile(r"<#(\d+)>")
USER_MATCH = re.compile(r"<@!?(\d+)>")

def normalise(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

async def preprocess_message_with_context(
    user_message: str,
    guild: discord.Guild
):
    # resolve user mentions to their usernames and channel mentions to their names
    # example: "<#67890>" -> "<#67890> (channelname)"
    # example: "<@12345>" -> "<@12345> (username)"
    content = user_message

    channel_mentions = re.findall(CHANNEL_MATCH, content)
    user_mentions = re.findall(USER_MATCH, content)

    for channel_id in channel_mentions:
        channel = guild.get_channel(int(channel_id))

        if not channel:
            continue

        content = content.replace(f"<#{channel_id}>", f"<#{channel_id}> ({channel.name})")
    
    for user_id in user_mentions:
        user = guild.get_member(int(user_id))

        if not user:
            continue

        content = content.replace(f"<@{user_id}>", f"<@{user_id}> ({user.display_name})")
        content = content.replace(f"<@!{user_id}>", f"<@!{user_id}> ({user.display_name})")

    return content
