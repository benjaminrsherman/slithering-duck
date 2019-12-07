from . import Command
from .. import utils


class Delete(Command, ReactionTrigger):
    prefixes = ["%"]
    requires_mod = True

    async def prompt_for_channel_deletion(command_channel, channel_to_delete, author):
        await command_channel.send(
            f"WARNING: You are about to delete <#{channel_to_delete.id}>.  <@{author.id}> can confirm this action by reacting :+1: to this message."
        ).add_reaction("👍")

    async def execute_command(self, client, msg, content):
        if not msg.author.guild_permissions.administrator:  # sorry joe
            msg.channel.send(client.messages["invalid_permissions"])
            return

        if not msg.channel_mentions:
            prompt_for_channel_deletion(msg.channel, msg.channel, msg.author)
            return

        for channel in msg.channel_mentions:
            prompt_for_channel_deletion(msg.channel, channel, msg.author)

    async def execute_reaction(self, client, reaction, channel, msg, user):
        if (
            reaction.emoji != "👍"  # reaction must be a :+1:
            or not msg.author.bot  # must be reacting to a bot message
            or user not in msg.user_mentions  # prevent misclicks
            or not msg.content.startswith(
                "WARNING: You are about to delete "
            )  # we must be deleting a channel
            or not msg.channel_mentions  # we need a channel to delete
            or not any(react.me and react.emoji == "👍")  # the bot must agree to this
        ):
            return

        channel_to_delete = msg.channel_mentions[0]  # only one channel per message

        # TODO:
        # - Mark channel as non-existent in database
        # - Send message to logging server indicating that the channel is now invalid
        # - Add logging equivalent to list of available logging server channels
        # - Delete channel from server

        await channel_to_delete.delete()
