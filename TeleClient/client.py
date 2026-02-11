from telethon import TelegramClient
from .env import OWNERS

class MyClient(TelegramClient):
    
    async def getMe(self):
        return await self.get_me()

    def checkOwner(self, event):
        return event.sender_id in OWNERS