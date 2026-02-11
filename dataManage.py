from motor import motor_asyncio
from env import MONGO_URI

# MongoDB Client setup
client = motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client["NewBot"]
collection = db["TelegramBot"]

# ============================ TELESESSION CLASS ============================ #
class TeleSession:
    def __init__(self) -> None:
        self.collection = collection

    async def add_session(self, userID: str, session: str):
        """Add a new session for a user."""
        check = await collection.find_one({"userID": userID})
        if check:
            if session in check["sessions"]:
                return None  # Session already exists
            else:
                await collection.update_one({"userID": userID}, {"$push": {"sessions": session}})
        else:
            await collection.insert_one({"userID": userID, "sessions": [session]})

    async def delete_session(self, userID: str, session: str):
        """Delete a specific session."""
        check = await collection.find_one({"userID": userID})
        if check:
            await collection.update_one({"userID": userID}, {"$pull": {"sessions": session}})
            return True
        return False

    async def delete_sessions(self, userID: str):
        """Delete all sessions for a user."""
        result = await collection.delete_one({"userID": userID})
        return result.deleted_count > 0

    async def get_sessions(self, userID: str):
        """Retrieve all sessions for a user."""
        allData = await collection.find_one({"userID": userID})
        return allData.get("sessions", None) if allData else None

# Inside dataManage.py

# Assuming userClients is a dictionary that stores user-client data
userClients = {}

def getClients(senderID):
    """Retrieve all clients for a given user."""
    return userClients.get(senderID, [])

# ============================ TELECHATLINKS CLASS ============================ #
class TeleChatLinks:
    def __init__(self) -> None:
        pass

    async def add_chat(self, userID: str, chat: str):
        """Add a chat link to a user's profile."""
        check = await collection.find_one({"userID": userID})
        if check:
            await collection.update_one({"userID": userID}, {"$push": {"chats": chat}})
        else:
            await collection.insert_one({"userID": userID, "chats": [chat]})

    async def delete_chat(self, userID: str, chat: str):
        """Delete a specific chat link from a user's profile."""
        check = await collection.find_one({"userID": userID})
        if check:
            await collection.update_one({"userID": userID}, {"$pull": {"chats": chat}})
            return True
        return False

    async def delete_chats(self, userID: str):
        """Delete all chat links for a user."""
        result = await collection.delete_one({"userID": userID})
        return result.deleted_count > 0

    async def get_chats(self, userID: str):
        """Get all chat links for a user."""
        allData = await collection.find_one({"userID": userID})
        return allData.get("chats", None) if allData else None

# ============================ TELEADS CLASS ============================ #
class TeleAds:
    def __init__(self) -> None:
        pass

    async def save_ad(self, userID: str, messageKey: str, messageID: str, sleepTime: str):
        """Save an advertisement for a user."""
        check = await collection.find_one({"userID": userID})
        if check:
            await collection.update_one({"userID": userID}, {"$set": {messageKey: {"messageID": messageID, "sleepTime": sleepTime}}})
        else:
            await collection.insert_one({"userID": userID, messageKey: {"messageID": messageID, "sleepTime": sleepTime}})

    async def delete_ad(self, userID: str, messageKey: str):
        """Delete a specific advertisement for a user."""
        check = await collection.find_one({"userID": userID})
        if check:
            await collection.update_one({"userID": userID}, {"$unset": {messageKey: ""}})
            return True
        return False

    async def delete_ads(self, userID: str):
        """Delete all advertisements for a user."""
        result = await collection.delete_one({"userID": userID})
        return result.deleted_count > 0

    async def get_ad(self, userID: str, messageKey: str):
        """Retrieve a specific advertisement for a user."""
        check = await collection.find_one({"userID": userID})
        if check:
            return check.get(messageKey, None)
        return None

    def rm_data(self, data: dict, keys: list):
        """Remove unwanted keys from the data."""
        for key in keys:
            data.pop(key, None)
        return data

    async def get_all_ads(self, userID: str):
        """Get all ads for a user, without unnecessary fields."""
        check = await collection.find_one({"userID": userID})
        if check:
            delete_keys = ["_id", "userID", "sessions"]
            return self.rm_data(check, delete_keys)
        return None

# ============================ TELELOGGING CLASS ============================ #
class TeleLogging:
    def __init__(self) -> None:
        pass

    async def set_logger(self, userID: str, chatID: str):
        """Set a logging chat ID for a user."""
        check = await collection.find_one({"_id": userID})
        if check:
            await collection.update_one({"_id": userID}, {"$set": {"chatID": chatID}})
        else:
            await collection.insert_one({"_id": userID, "chatID": chatID})

    async def get_logger(self, userID: str):
        """Get the logging chat ID for a user."""
        check = await collection.find_one({"_id": userID})
        if check:
            return check.get("chatID", None)
        return None

    async def chat_ids(self):
        """Get all chat IDs for all users with logging enabled."""
        cursor = collection.find({}, {"chatID": 1, "_id": 0})
        chat_ids = []
        async for document in cursor:
            if "chatID" in document:
                chat_ids.append(document["chatID"])
        return chat_ids

    async def delete_logger(self, userID: str):
        """Delete a user's logging chat ID."""
        check = await collection.find_one({"_id": userID})
        if check:
            await collection.update_one({"_id": userID}, {"$unset": {"chatID": ""}})
            return True
        return False

# ============================ TELESUDO CLASS ============================ #
class TeleSudo:
    def __init__(self) -> None:
        pass

    async def add_sudo(self, userID: str):
        """Add a user to the sudo list."""
        check = await collection.find_one({"_id": "sudo"})
        if check:
            if userID not in check["sudo"]:
                await collection.update_one({"_id": "sudo"}, {"$push": {"sudo": userID}})
        else:
            await collection.insert_one({"_id": "sudo", "sudo": [userID]})

    async def delete_sudo(self, userID: str):
        """Remove a user from the sudo list."""
        check = await collection.find_one({"_id": "sudo"})
        if check:
            if userID in check["sudo"]:
                await collection.update_one({"_id": "sudo"}, {"$pull": {"sudo": userID}})
            return True
        return False

    async def get_sudos(self):
        """Retrieve the list of sudo users."""
        check = await collection.find_one({"_id": "sudo"})
        if check:
            return [int(sudo) for sudo in check["sudo"]]
        return []

# Inside dataManage.py

# Example of saving a sudo user (could be saving to a database or memory)
SUDO_USERS = []

def saveSudo(userID):
    """Save a user as a sudo."""
    if userID not in SUDO_USERS:
        SUDO_USERS.append(userID)

def delSudo(userID):
    """Remove a user from sudo list."""
    if userID in SUDO_USERS:
        SUDO_USERS.remove(userID)

def getSudo(userID):
    """Check if a user is a sudo."""
    return userID in SUDO_USERS

def getSudos():
    """Return the list of sudo users."""
    return SUDO_USERS

# ============================ TELESAVEUSER CLASS ============================ #
class SaveUser:
    def __init__(self) -> None:
        pass

    async def save_user(self, userID: str):
        """Save a user to the database."""
        check = await collection.find_one({"_id": "users"})
        if check:
            if userID not in check["users"]:
                await collection.update_one({"_id": "users"}, {"$push": {"users": userID}})
        else:
            await collection.insert_one({"_id": "users", "users": [userID]})

    async def delete_user(self, userID: str):
        """Delete a user from the database."""
        check = await collection.find_one({"_id": "users"})
        if check:
            await collection.update_one({"_id": "users"}, {"$pull": {"users": userID}})
            return True
        return False

    async def get_users(self):
        """Retrieve all saved users."""
        check = await collection.find_one({"_id": "users"})
        if check:
            return [int(user) for user in check["users"]]
        return []