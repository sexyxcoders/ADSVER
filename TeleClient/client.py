from telethon import TelegramClient
from env import OWNERS   # If env.py is in root project

class MyClient(TelegramClient):

    def __init__(self, session, api_id, api_hash):
        super().__init__(session, api_id, api_hash)
        self.me = None

    # Get bot info
    async def getMe(self):
        self.me = await self.get_me()
        return self.me

    # Owner check
    def checkOwner(self, event):
        return event.sender_id in OWNERS

    # Cancel keyword checker
    async def checkCancel(self, text):
        if not text:
            return False
        text = str(text).lower()
        return text in ["cancel", "/cancel", "stop", "exit"]

    # Override start to auto set self.me
    async def start(self, *args, **kwargs):
        await super().start(*args, **kwargs)
        await self.getMe()
        return self