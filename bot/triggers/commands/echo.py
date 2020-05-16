import discord

from . import Command
from .. import utils
from ...duck import DuckClient


class Echo(Command):
    names = ["echo", "repeat"]
    description = "Echoes the given message"
    usage = "!echo [message]"

    async def execute_command(
        self, client: DuckClient, msg: discord.Message, content: str
    ) -> None:
        if content:
            content.replace("@everyone", "@\u200beveryone")
            content.replace("@here", "@\u200bhere")
        else:
            content = "_ _"  # renders as invisible
        await utils.delay_send(msg.channel, content)
