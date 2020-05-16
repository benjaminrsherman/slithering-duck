from typing import cast, Optional, Union

import discord

from . import Command
from .. import utils
from ..reaction_trigger import ReactionTrigger
from ...logging import get_log_channel
from ...duck import DuckClient


class Delete(Command, ReactionTrigger):
    prefixes = ["%", "sudo rm -f"]
    names = ["delete"]
    description = "ADMIN ONLY: Deletes a channel"
    requires_mod = True

    def __init__(self) -> None:
        self.thumb: Optional[discord.Emoji] = None

    async def prompt_for_channel_deletion(
        self,
        client: DuckClient,
        command_channel: discord.TextChannel,
        channel_to_delete: discord.TextChannel,
        author: discord.Member,
    ) -> None:
        async with client.log_lock:
            client.cursor.execute(
                "SELECT * FROM classes WHERE channel_id = :channel_id",
                {"channel_id": channel_to_delete.id},
            )
            if not client.cursor.fetchall():
                await utils.delay_send(
                    command_channel,
                    f"ERROR: <#{channel_to_delete.id}> is not a class channel",
                )
                return

        msg = await utils.delay_send(
            command_channel,
            f"WARNING: You are about to delete <#{channel_to_delete.id}>.  <@{author.id}> can confirm this action by reacting :+1: to this message.",
        )

        if not self.thumb:
            thumb_emoji = client.get_emoji(client.config["thumb_id"])
            if not thumb_emoji:
                raise AttributeError(
                    "Tried to use %delete when not configured.  Make sure 'thumb_id' in config is properly set."
                )
            self.thumb = thumb_emoji

        await msg.add_reaction(self.thumb)

    async def execute_command(
        self, client: DuckClient, msg: discord.Message, content: str
    ) -> None:
        if not client.config["ENABLE_COURSES"]:
            await utils.delay_send(
                msg.channel,
                "ERROR: I have been configured to not support courses.  Aborting...",
            )
            return

        msg.author = cast(discord.Member, msg.author)
        if not msg.author.guild_permissions.administrator:
            utils.delay_send(msg.channel, client.messages["invalid_permissions"])
            return

        msg.channel = cast(discord.TextChannel, msg.channel)

        if not msg.channel_mentions:
            await self.prompt_for_channel_deletion(
                client, msg.channel, msg.channel, msg.author,
            )
            return

        for channel in msg.channel_mentions:
            await self.prompt_for_channel_deletion(
                client, msg.channel, channel, msg.author,
            )

    async def execute_reaction(
        self,
        client: DuckClient,
        reaction: discord.RawReactionActionEvent,
        channel: discord.TextChannel,
        msg: discord.Message,
        user: discord.User,
    ) -> bool:
        if (  # pylint: disable=too-many-boolean-expressions
            reaction.emoji.id != client.config["thumb_id"]  # reaction must be a :+1:
            or not msg.author.bot  # must be reacting to a bot message
            or user not in msg.mentions  # prevent misclicks
            or not msg.content.startswith(
                "WARNING: You are about to delete "
            )  # we must be deleting a channel
            or not msg.channel_mentions  # we need a channel to delete
            or not any(
                react.me and react.emoji.id == client.config["thumb_id"]
                for react in msg.reactions
                if isinstance(react.emoji, (discord.Emoji, discord.PartialEmoji))
            )  # the bot must agree to this
        ):
            return False

        await msg.clear_reactions()

        channel_to_delete = msg.channel_mentions[0]  # only one channel per message
        log_equivalent = await get_log_channel(channel_to_delete, client)
        deleted_id = channel_to_delete.id
        deleted_name = channel_to_delete.name

        async with client.lock:
            await channel_to_delete.delete()

            client.cursor.execute(
                "UPDATE classes SET channel_id = 0 WHERE channel_id = :channel_id;",
                {"channel_id": deleted_id},
            )
            client.connection.commit()

        async with client.log_lock:
            client.log_c.execute(
                "INSERT INTO unused_logging VALUES (:channel_id);",
                {"channel_id": log_equivalent.id},
            )
            client.log_c.execute(
                "DELETE FROM logging WHERE dest_channel_id = (:channel_id);",
                {"channel_id": log_equivalent.id},
            )
            client.log_connection.commit()

        await log_equivalent.send(f"CHANNEL WAS: {deleted_name}")

        if channel_to_delete.id != msg.channel.id:
            await utils.delay_send(msg.channel, "DELETED {deleted_name}")

        return True
