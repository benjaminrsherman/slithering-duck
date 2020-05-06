# THIS FILE ONLY HANDLES MESSAGE INTERACTION (DEALING WITH AND RESPONDING TO
# MESSAGES VIOLATING THE EMOJI-MODE STATUS)
#
# PLEASE SEE `commands/emoji_mode.py` FOR MODIFYING THE EMOJI-MODE STATE

import re

from discord import ChannelType, HTTPException
import emoji
import requests

from . import utils


# emotes are of the form <:emote_name:1234> where `1234` is the emote's id
DISCORD_EMOTE_RE = re.compile(r"<a?:[\w]+?:(\d+?)>")
DISCORD_EMOTE_ID_RE = re.compile(f":(\d+)>")
NESTED_EMOTE_RE = re.compile(r"<[^>]+<")

INVALID_EMOJI_RE = re.compile(
    "🇦|🇧|🇨|🇩|🇪|🇫|🇬|🇮|🇯|🇰|🇱|🇲|🇳|🇴|🇵|🇷|🇸|🇹|🇺|🇻|🇼|🇽|🇾|🇿|🇶|:regional_indicator_[a-zA-Z]+?:"
)

# explains to the violator why their message was deleted
async def send_message_to_violator(client, user):
    try:
        await user.send(client.messages["emoji_mode_dm"])
    except HTTPException:
        pass


# validates a single discord emote by verifying that its id is a real emote
# id. if the emote is valid, it will return an empty string to remove the
# emote from the message content.  If the emote is invalid, the content string
# will be unmodified.
def validate_discord_emote(emote) -> str:
    emote_id = DISCORD_EMOTE_ID_RE.search(str(emote)).group(1)
    if requests.get(f"https://cdn.discordapp.com/emojis/{emote_id}").status_code == 200:
        # valid emote
        return ""
    else:
        # invalid emote
        return emote


# returns true if the message only contains emoji and whitespace.  It will
# validate discord emotes as well.
def valid_emoji(content, msg) -> bool:
    if len(msg.embeds) or len(msg.attachments) or NESTED_EMOTE_RE.match(content):
        return False

    content = DISCORD_EMOTE_RE.sub(validate_discord_emote, content)
    content = INVALID_EMOJI_RE.sub("a", content)
    content = emoji.get_emoji_regexp().sub("", content)

    return len(content.split()) == 0  # calling split() discounts whitepace


# deletes message if the message is invalid
# returns true if the message was deleted
async def invalid_emoji_message(client, msg) -> bool:
    if msg.channel.type is ChannelType.private or msg.channel.type is ChannelType.group:
        return False

    hits = 0

    async with client.lock:
        client.cursor.execute(
            "SELECT count(*) FROM emoji_channels WHERE channel_id = :chann_id",
            {"chann_id": msg.channel.id},
        )
        hits += client.cursor.fetchone()[0]

    async with client.lock:
        client.cursor.execute(
            "SELECT count(*) FROM emoji_users WHERE user_id = :author_id",
            {"author_id": msg.author.id},
        )
        hits += client.cursor.fetchone()[0]

    if hits > 0:
        if utils.user_is_mod(client, msg.author):
            return False

        if not valid_emoji(msg.content, msg):
            await msg.delete()
            await send_message_to_violator(client, msg.author)
            return True
    return False
