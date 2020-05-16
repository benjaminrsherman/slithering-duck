import re
from typing import List, Optional, Tuple

from fuzzywuzzy import fuzz
import discord

from .. import utils
from ..message_trigger import MessageTrigger
from ...duck import DuckClient


# Import all command classes here
from .ai import AI
from .choice import Choice
from .class_management import AddClass, RemoveClass
from .code import Code
from .connectfour import ConnectFour
from .cpp_ref import CppRef
from .delete import Delete
from .echo import Echo
from .emoji_mode import EmojiMode
from .java import Java  # type: ignore
from .issue import Issue
from .latex import Latex  # latex machine broke
from .list_classes import ListClasses
from .lmdtfy import Lmdtfy, Lmgtfy
from .man import Man
from .math import Math
from .minesweeper import Minesweeper
from .poll import Poll
from .rand import Random
from .rgb import RGB
from .rps import RockPaperScissors
from .steam import Steam
from .tictactoe import TicTacToe
from .translate import Translate
from .version import Version
from .wikipedia import Wikipedia
from .xkcd import Xkcd

# NB: Please keep this in alphabetical order to maintain organized code
ALL_COMMANDS = [
    AddClass(),
    AI(),
    Choice(),
    Code(),
    ConnectFour(),
    CppRef(),
    Delete(),
    Echo(),
    EmojiMode(),
    Java(),
    Issue(),
    Latex(),
    ListClasses(),
    Lmdtfy(),
    Lmgtfy(),
    Man(),
    Math(),
    Minesweeper(),
    Poll(),
    Random(),
    RemoveClass(),
    RGB(),
    RockPaperScissors(),
    Steam(),
    TicTacToe(),
    Translate(),
    Version(),
    Wikipedia(),
    Xkcd(),
]


class Command(MessageTrigger):
    names: List[str] = []
    prefixes = ["!"]
    requires_mod = False
    should_type = True
    causes_spam = False

    async def is_valid(self, msg: discord.Message) -> Tuple[Optional[int], float]:
        command = ""

        max_ratio = 0
        for name in self.names:
            for prefix in self.prefixes:
                if re.match(f"^{prefix}{name}\\b", msg.content.lower()):
                    command = prefix + name
                    max_ratio = 1  # exact match
                    break
                if msg.content.lower().startswith(prefix):
                    ratio = fuzz.ratio(
                        msg.content.lower().split()[0], f"{prefix}{name}"
                    )
                    max_ratio = ratio if ratio > max_ratio else max_ratio
            if command:
                break

        if command == "" and len(msg.content.lower()) > 0:
            command = msg.content.lower().split()[0]

        if max_ratio != 1:
            return (None, max_ratio)

        return (len(command), 1)

    async def get_trigger_score(
        self, client: DuckClient, msg: discord.Message
    ) -> Tuple[float, Optional[int]]:
        (idx, recognized) = await self.is_valid(msg)

        return recognized, idx

    async def execute_message(
        self, client: DuckClient, msg: discord.Message, idx: int
    ) -> None:
        if self.requires_mod and not utils.user_is_mod(client, msg.author):
            await utils.delay_send(msg.channel, client.messages["invalid_permissions"])
            return

        # checks if a trigger causes spam and then if that trigger should run given the channel it was sent in
        # any command without self.causes_spam will cause an exception and skip this to run like normal
        if (
            self.causes_spam
            and msg.channel.type is not discord.ChannelType.private
            and msg.channel.id not in client.config["spam_channel_ids"]
        ):
            channel_tags = ""
            for chann_id in client.config["spam_channel_ids"]:
                channel_tags += f" <#{chann_id}>"
            await utils.delay_send(
                msg.channel,
                client.messages["send_to_spam_channel"].format(channel_tags),
            )
            return

        # The execute command is defined here to decrease code reuse below
        async def _execute() -> None:
            await self.execute_command(
                client, msg, utils.sanitized(msg.clean_content[idx:].strip())
            )

        if self.should_type:
            async with msg.channel.typing():
                await _execute()
        else:
            await _execute()

    async def execute_command(
        self, client: DuckClient, msg: discord.Message, content: str
    ) -> None:
        raise NotImplementedError("'execute_command' not implemented for this command")

    def __lt__(self, other: Command) -> bool:
        return self.names[0] < other.names[0]


async def invalid_command(client: DuckClient, msg: discord.Message) -> bool:
    if msg.author.bot or len(msg.content) < 2 or msg.content[0] != "!":
        return False

    await utils.delay_send(
        msg.channel,
        client.messages["invalid_command"].format(utils.sanitized(msg.content.strip())),
    )
    return True
