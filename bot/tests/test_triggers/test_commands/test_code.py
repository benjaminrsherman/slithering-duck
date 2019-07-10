import unittest
import json
from ... import test_utils
from ....triggers.commands import code
from ....duck import DuckClient


class TestCode(unittest.TestCase):
    def setUp(self):
        self.code = code.Code()
        with open("config/messages.json", "r") as messages_file:
            messages = json.load(messages_file)
            self.code_message = messages["code"]
        self.client = DuckClient()

    @test_utils.async_test
    async def test_ai(self):
        msg = test_utils.init_message(f"!code")
        self.assertTrue(
            await self.code.execute(
                self.client, msg
            )  # `client` is passed as None because it is never used
        )
        self.assertEqual(msg.channel.test_result, self.code_message)
