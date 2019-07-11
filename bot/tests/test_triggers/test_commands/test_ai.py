import unittest
import json
from ... import test_utils
from ....triggers.commands import ai
from ....duck import DuckClient


class TestAI(unittest.TestCase):
    def setUp(self):
        self.ai = ai.AI()
        with open("config/messages.json", "r") as messages_file:
            messages = json.load(messages_file)
            self.ai_message = messages["academic_integrity"]
        self.client = DuckClient()

    @test_utils.async_test
    async def test_ai(self):
        test_strings = ["ai", "academic integrity"]
        for string in test_strings:
            msg = test_utils.init_message(f"!{string}")
            self.assertTrue(await self.ai.execute(self.client, msg))
            self.assertEqual(msg.channel.test_result, self.ai_message)
