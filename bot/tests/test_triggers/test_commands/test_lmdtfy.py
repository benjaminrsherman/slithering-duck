import unittest
from urllib.parse import urlencode

from ... import test_utils
from ....triggers.commands import lmdtfy


class TestLmdtfy(unittest.TestCase):
    def setUp(self):
        self.lmdtfy = lmdtfy.Lmdtfy()
        self.lmgtfy = lmdtfy.Lmgtfy()

    @test_utils.async_test
    async def test_lmdtfy(self):
        test_strings = ["abcd", "hello world!", "הברווז אומר היי"]
        for string in test_strings:
            msg = test_utils.init_message(f"!lmdtfy {string}")
            self.assertTrue(
                await self.lmdtfy.execute(
                    None, msg
                )  # `client` is passed as None because it is never used
            )
            url = "https://lmgtfy.com/?s=d&" + urlencode({"q": string})
            self.assertEqual(msg.channel.test_result, url)

    @test_utils.async_test
    async def test_lmgtfy(self):
        test_strings = ["abcd", "hello world!", "הברווז אומר היי"]
        for string in test_strings:
            msg = test_utils.init_message(f"!lmgtfy {string}")
            self.assertTrue(
                await self.lmgtfy.execute(
                    None, msg
                )  # `client` is passed as None because it is never used
            )
            url = "https://lmgtfy.com/?" + urlencode({"q": string})
            self.assertEqual(msg.channel.test_result, url)

    @test_utils.async_test
    async def test_lmdtfy_empty(self):
        for num_spaces in range(0, 10):
            msg = test_utils.init_message(f"!lmdtfy" + " " * num_spaces)
            self.assertFalse(
                await self.lmdtfy.execute(
                    None, msg
                )  # `client` is passed as None because it is never used
            )

    @test_utils.async_test
    async def test_lmgtfy_empty(self):
        for num_spaces in range(0, 10):
            msg = test_utils.init_message(f"!lmgtfy" + " " * num_spaces)
            self.assertFalse(
                await self.lmgtfy.execute(
                    None, msg
                )  # `client` is passed as None because it is never used
            )
