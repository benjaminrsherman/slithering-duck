import unittest
import discord
from ... import test_utils
from ....triggers.commands import all_commands
from ....duck import DuckClient


class TestHelp(unittest.TestCase):
    def setUp(self):
        self.client = DuckClient()
        self.client._connection.user = test_utils.MockUser()

    @test_utils.async_test
    async def test_help(self):
        msg = test_utils.init_message("!help")
        await self.client.on_message(msg)
        expected_help = discord.Embed()
        commands_str = ""
        for command in all_commands:
            commands_str += (
                f"**{command.prefixes[0]}{command.names[0]}:** {command.description}\n"
            )
        expected_help.add_field(
            name="General Commands", value=commands_str, inline=True
        )
        self.assertEqual(msg.channel.embed_dict, expected_help.to_dict())
        self.assertEqual(msg.channel.test_result, "")
        self.assertIsNone(msg.channel.filename)

    @test_utils.async_test
    async def test_help_from_bot(self):
        msg = test_utils.init_message("!help")
        msg.author.bot = True
        await self.client.on_message(msg)
        self.assertIsNone(msg.channel.test_result)
        self.assertIsNone(msg.channel.embed_dict)
        self.assertIsNone(msg.channel.filename)
