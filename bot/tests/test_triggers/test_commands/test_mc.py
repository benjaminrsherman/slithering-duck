import unittest
import json
import requests
import discord
from ... import test_utils
from ....triggers.commands import minecraft
from ....duck import DuckClient


class TestMinecraft(unittest.TestCase):
    def setUp(self):
        self.mc = minecraft.Minecraft()
        with open("config/config.json", "r") as config_file:
            config = json.load(config_file)
            self.minecraft = config["minecraft"]
        self.client = DuckClient()

    @test_utils.async_test
    async def test_ai(self):
        test_strings = ["mc", "minecraft"]
        for string in test_strings:
            msg = test_utils.init_message(f"!{string}")
            mock_usr = test_utils.MockUser()
            mock_usr.display_name = "testy_mc_test_face"
            msg.channel.guild.members[int(self.minecraft["host_id"])] = mock_usr

            self.assertTrue(await self.mc.execute(self.client, msg))

            data = requests.get(
                url="https://mcapi.us/server/status",
                params={"ip": self.minecraft["ip"]},
            ).json()
            description = (
                "**IP: ** "
                + self.minecraft["ip"]
                + "\n**Status: ** "
                + data["status"]
                + "\n**Players: ** "
                + str(data["players"]["now"])
                + "/"
                + str(data["players"]["max"])
            )
            expected_embed = discord.Embed(description=description, color=0x3E5C20)
            expected_embed.set_author(
                name="⁠",
                icon_url="https://discordemoji.com/assets/emoji/grassblock.png",
            )
            expected_embed.set_footer(
                text="Minecraft server is courtesy of @testy_mc_test_face"
            )

            self.assertEqual(msg.channel.embed_dict, expected_embed.to_dict())
