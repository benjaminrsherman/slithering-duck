import unittest
from ... import test_utils
from ....triggers.commands import translate


class TestTranslate(unittest.TestCase):
    def setUp(self):
        self.translate = translate.Translate()

    @test_utils.async_test
    async def test_translate(self):
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
    async def test_translate_empty(self):
        for num_spaces in range(0, 10):
            msg = test_utils.init_message("!translate" + " " * num_spaces)
            self.assertFalse(
                await self.translate.execute(
                    None, msg
                )  # `client` is passed as None because it is never used
            )
            self.assertIsNone(msg.channel.test_result)
