import random
from typing import Union

import discord

from . import Command
from .. import utils

from ...duck import DuckClient


class Random(Command):
    names = ["random", "rand"]
    description = "Returns a random float or integer with specified parameters"
    usage = "!random [(optional) int/float] [(optional) num1] [(optional) num2]"
    examples = "!random, !random 1 10, !random float 1 10"
    notes = "By default, this returns a float in the range [0,1).  If given arguments, it'll try to match the type of the argument"

    async def execute_command(
        self, client: DuckClient, msg: discord.Message, content: str
    ) -> None:
        if len(content) == 0:
            await utils.delay_send(msg.channel, str(random.random()))
            return

        args = content.split()

        if len(args) == 2:
            arg1_idx = 0
        else:
            arg1_idx = 1

        try:
            try:
                arg1: Union[int, float] = int(args[arg1_idx])
                arg2: Union[int, float] = int(args[arg1_idx + 1])
            except ValueError:
                arg1 = float(args[arg1_idx])
                arg2 = float(args[arg1_idx + 1])
        except (IndexError, ValueError):
            await utils.delay_send(msg.channel, f"Usage: {self.usage}")
            return

        min_val = min(arg1, arg2)
        max_val = max(arg1, arg2)

        # Only generate an integer if we're given integers or the user wants it
        if args[0] == "int" or isinstance(arg1, int):
            random_val: Union[int, float] = random.randint(int(min_val), int(max_val))
        else:
            random_val = random.uniform(min_val, max_val)

        await utils.delay_send(msg.channel, str(random_val))
