from telethon import TelegramClient
from .env import OWNERS

from telethon import TelegramClient

class MyClient(TelegramClient):

    async def init_me(self):
        self.me = await self.get_me()

    async def checkCancel(self, text):
        return str(text).lower() in ["cancel", "stop", "/cancel", "exit"]

class MyClient(TelegramClient):
    
    async def getMe(self):
        return await self.get_me()

    def checkOwner(self, event):
        return event.sender_id in OWNERS

async def start(self, *args, **kwargs):
    await super().start(*args, **kwargs)
    self.me = await self.get_me()
    return self