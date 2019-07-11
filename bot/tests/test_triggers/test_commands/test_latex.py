import unittest
import json
import requests
import re
import urllib
from PIL import Image, ImageOps
import os
import math
from functools import reduce
import operator

from ... import test_utils
from ....triggers.commands import latex
from ....duck import DuckClient


class TestLatex(unittest.TestCase):
    def setUp(self):
        self.latex = latex.Latex()

    @test_utils.async_test
    async def test_latex(self):
        test_strings = ["$quack$", "\\Sigma"]
        for string in test_strings:
            msg = test_utils.init_message(f"!tex {string}")
            self.assertTrue(
                await self.latex.execute(
                    None, msg
                )  # `client` is passed as None because it is never used
            )

            data = requests.post(
                url="http://latex2png.com/",
                data={"latex": string, "res": 600, "color": "FFFFFF", "x": 62, "y": 28},
            )
            # print(data.text)
            name = re.search(r"latex_(.*)\.png", data.text).group()
            if name:
                url = f"http://latex2png.com/output//{name}"
                tmpLocation = f"/tmp/{name}"
                urllib.request.urlretrieve(url, tmpLocation)

                expected_img = Image.open(tmpLocation)
                borderSizeX, borderSizeY = expected_img.size
                borderSizeX = math.ceil(borderSizeX / 20)
                borderSizeY = 0
                expected_img_with_border = ImageOps.expand(
                    expected_img,
                    border=(borderSizeX, borderSizeY, borderSizeX, borderSizeY),
                    fill="#00000000",
                )

                self.assertIsNotNone(msg.channel.filename)
                h1 = expected_img.histogram()
                h2 = Image.open(msg.channel.filename).histogram()

                self.assertEqual(len(h1), len(h2))

                rms = math.sqrt(
                    reduce(operator.add, map(lambda a, b: (a - b) ** 2, h1, h2))
                    / len(h1)
                )

                self.assertTrue(rms < 150)

                os.remove(msg.channel.filename)

    @test_utils.async_test
    async def test_latex_empty(self):
        for num_spaces in range(0, 10):
            msg = test_utils.init_message("!tex" + " " * num_spaces)
            self.assertFalse(
                await self.latex.execute(
                    None, msg
                )  # `client` is passed as None because it is never used
            )
