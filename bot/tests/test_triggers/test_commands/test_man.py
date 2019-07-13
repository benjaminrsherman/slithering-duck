import unittest
from ... import test_utils
from ....triggers.commands import man


class TestMan(unittest.TestCase):
    def setUp(self):
        self.man = man.Man()

    @test_utils.async_test
    async def test_man_valid(self):
        test_strings = [
            ("https://linux.die.net/man/1/free", "free"),
            ("https://linux.die.net/man/3/fgets", "fgets"),
            ("https://linux.die.net/man/3/free", "3 free"),
        ]
        for string in test_strings:
            msg = test_utils.init_message(f"!man {string[1]}")
            self.assertTrue(
                await self.man.execute(
                    None, msg
                )  # `client` is passed as None because it is never used
            )
            self.assertEqual(msg.channel.test_result, string[0])

    @test_utils.async_test
    async def test_man_invalid(self):
        test_strings = ["abcd", "2 echo", "3"]
        for string in test_strings:
            msg = test_utils.init_message(f"!man {string}")
            self.assertTrue(
                await self.man.execute(
                    None, msg
                )  # `client` is passed as None because it is never used
            )
            self.assertEqual(
                msg.channel.test_result, f"Could not find man page for `{string}`"
            )

    @test_utils.async_test
    async def test_man_empty(self):
        for num_spaces in range(0, 10):
            msg = test_utils.init_message("!man" + " " * num_spaces)
            self.assertFalse(
                await self.man.execute(
                    None, msg
                )  # `client` is passed as None because it is never used
            )
            self.assertIsNone(msg.channel.test_result)
