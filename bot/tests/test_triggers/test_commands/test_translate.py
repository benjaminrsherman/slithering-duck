import unittest
from ... import test_utils
from ....triggers.commands import translate


class TestTranslate(unittest.TestCase):
    def setUp(self):
        self.translate = translate.Translate()

    @test_utils.async_test
    async def test_translate_one_message(self):
        test_strings = [
            ("我是一隻鴨子", '"我是一隻鴨子" translates from ZH-CN to: `I am a duck`'),
            (
                "אני ברווז גומי",
                '"אני ברווז גומי" translates from IW to: `I\'m a rubber duck`',
            ),
            (
                "Rwy'n robot hwyaden rwber",
                "\"Rwy'n robot hwyaden rwber\" translates from CY to: `I'm a rubber duck robot`",
            ),
            (
                "The rubber duck says quack",
                '"The rubber duck says quack" translates from EN to: `The rubber duck says quack`',
            ),
        ]
        for string in test_strings:
            msg = test_utils.init_message(f"!translate {string[0]}")
            self.assertTrue(
                await self.translate.execute(
                    None, msg
                )  # `client` is passed as None because it is never used
            )
            self.assertEqual(msg.channel.test_result, string[1])

    @test_utils.async_test
    async def test_translate_multiple_messages(self):
        test_input = "我是一隻鴨子"
        expected_output = '"我是一隻鴨子" translates from ZH-CN to: `I am a duck`'

        msg = test_utils.init_message(test_input)
        msg2 = test_utils.init_message("!translate")
        msg2.channel = msg.channel
        msg2.id = 1
        msg2.channel.internal_history.append(msg2)

        self.assertTrue(
            await self.translate.execute(
                None, msg2
            )  # `client` is passed as None because it is never used
        )
        self.assertEqual(msg2.channel.test_result, expected_output)
