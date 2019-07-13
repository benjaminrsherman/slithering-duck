import unittest
import discord
from ... import test_utils
from ....triggers.commands import help, all_commands


class TestHelp(unittest.TestCase):
    def setUp(self):
        self.help = help.Help()

    @test_utils.async_test
    async def test_help(self):
        msg = test_utils.init_message(f"!help")
        self.assertTrue(
            await self.help.execute(
                None, msg
            )  # `client` is passed as None because it is never used
        )
        expected_help = discord.Embed()
        commands_str = ""
        for command in all_commands:
            commands_str += f"**{command.names[0]}:** {command.description}\n"
        expected_help.add_field(
            name="General Commands", value=commands_str, inline=True
        )
        self.assertEqual(msg.channel.embed_dict, expected_help.to_dict())
