import asyncio
import shutil


def async_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)

    return wrapper


import discord


class MockTyping:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return


class HistoryIter:
    def __init__(self, msgs):
        self.msgs = msgs

    async def __aiter__(self):
        for msg in self.msgs:
            yield msg


class MockChannel:
    def __init__(self):
        self.test_result = None
        self.id = 0
        self.internal_history = []

    async def send(self, message="", file=None):
        self.test_result = message
        if file is not None:
            fname = file.fp.name
            new_fname = f"{fname}_test"
            shutil.copyfile(fname, new_fname)
            self.filename = new_fname
            file.close()
        else:
            self.filename = None

    def typing(self):
        return MockTyping()

    def history(self, limit=0):
        return HistoryIter(self.internal_history[:limit])


class MockUser:
    def __init__(self):
        self.bot = False
        self.id = 0


class MockMessage:
    def __init__(self):
        self.id = 0


def init_message(content):
    message = MockMessage()
    message.author = MockUser()
    message.channel = MockChannel()
    message.content = content
    return message
