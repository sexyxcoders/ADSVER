from motor import motor_asyncio
from env import MONGO_URI

client = motor_asyncio.AsyncIOMotorClient(MONGO_URI)

db = client["NewBot"]

collection = db["TelegramBot"]


class TeleSession:
    def __init__(self) -> None:
        self.collection = collection
        pass

    async def add_session(self, userID: str, session: str):
        check = await collection.find_one({"userID": userID})
        if check:
            if session in check["sessions"]:
                return None
            else:
                await collection.update_one({"userID": userID}, {"$push": {"sessions": session}})
        else:
            await collection.insert_one({"userID": userID, "sessions": [session]})

    async def delete_session(self, userID: str, session: str):
        check = await collection.find_one({"userID": userID})
        if check:
            await collection.update_one({"userID": userID}, {"$pull": {"sessions": session}})
        else:
            return False

    async def delete_sessions(self, userID: str):
        await collection.delete_one({"userID": userID})

    async def get_sessions(self, userID: str):
        allData = await collection.find_one({"userID": userID})
        try:
            return allData["sessions"]
        except:
            return None


class TeleChatLinks:
    def __init__(self) -> None:
        pass

    async def add_chat(self, userID: str, chat: str):
        check = await collection.find_one({"userID": userID})
        if check:
            await collection.update_one({"userID": userID}, {"$push": {"chats": chat}})
        else:
            await collection.insert_one({"userID": userID, "chats": [chat]})

    async def delete_chat(self, userID: str, chat: str):
        check = await collection.find_one({"userID": userID})
        if check:
            await collection.update_one({"userID": userID}, {"$pull": {"chats": chat}})
        else:
            return False

    async def delete_chats(self, userID: str):
        await collection.delete_one({"userID": userID})

    async def get_chats(self, userID: str):
        allData = await collection.find_one({"userID": userID})
        return allData["chats"]


class TeleAds:
    def __init__(self) -> None:
        pass
    
    async def save_ad(self, userID: str, messageKey: str, messageID: str, sleepTime: str):
        check = await collection.find_one({"userID": userID})
        if check:
            await collection.update_one({"userID": userID}, {"$set": {messageKey: {"messageID": messageID, "sleepTime": sleepTime}}})
        else:
            await collection.insert_one({"userID": userID, messageKey: {"messageID": messageID, "sleepTime": sleepTime}})
            
        
    async def delete_ad(self, userID: str, messageKey: str):
        check = await collection.find_one({"userID": userID})
        if check:
            await collection.update_one({"userID": userID}, {"$unset": {messageKey: ""}})
        else:
            return False

    async def delete_ads(self, userID: str):
        await collection.delete_one({"userID": userID})

    async def get_ad(self, userID: str, messageKey: str):
        check = await collection.find_one({"userID": userID})
        if check:
            return check[messageKey]
        else:
            return None
        
    def rm_data(self, data:dict, keys:list):
        for key in keys:
            data.pop(key)
        return
    
    async def get_all_ads(self, userID: str):
        check = await collection.find_one({"userID": userID})
        if check:
            delete_keys = [
                "_id",
                "userID",
                "sessions"
            ]
            self.rm_data(check, delete_keys)
            return check
        else:
            return None
        

class TeleLogging:
    def __init__(self) -> None:
        pass

    async def set_logger(self, userID: str, chatID: str):
        check = await collection.find_one({"_id": userID})
        if check:
            await collection.update_one({"_id": userID}, {"$set": {"chatID": chatID}})
        else:
            await collection.insert_one({"_id": userID, "chatID": chatID})

    async def get_logger(self, userID: str):
        check = await collection.find_one({"_id": userID})
        if check:
            return check["chatID"]
        else:
            return None
        
    async def chat_ids(self):
        cursor = collection.find({}, {"chatID": 1, "_id": 0})
        chat_ids = []
        async for document in cursor:
            if "chatID" in document:
                chat_ids.append(document["chatID"])
        return chat_ids
    
    async def delete_logger(self, userID: str):
        check = await collection.find_one({"_id": userID})
        if check:
            await collection.update_one({"_id": userID}, {"$unset": {"chatID": ""}})
        else:
            return False


class TeleSudo:
    def __init__(self) -> None:
        pass

    async def add_sudo(self, userID: str):
        check = await collection.find_one({"_id": "sudo"})
        if check:
            if userID in check["sudo"]:
                return None
            else:
                await collection.update_one({"_id": "sudo"}, {"$push": {"sudo": userID}})
        else:
            await collection.insert_one({"_id": "sudo", "sudo": [userID]})

        

    async def delete_sudo(self, userID: str):
        check = await collection.find_one({"_id": "sudo"})
        if check:
            await collection.update_one({"_id": "sudo"}, {"$pull": {"sudo": userID}})
        else:
            return False
    
    async def get_sudos(self):
        check = await collection.find_one({"_id": "sudo"})
        if check:
            sudoList = [int(sudo) for sudo in check["sudo"]]
            return sudoList
        else:
            return []
        

class TeleDebug:
    def __init__(self) -> None:
        pass

    async def set_debug(self, myID):
        check = await collection.find_one({"_id": "debug"})
        if check:
            if myID in check["debug"]:
                return None
            else:
                await collection.update_one({"_id": "debug"}, {"$push": {"debug": myID}})
        else:
            await collection.insert_one({"_id": "debug", "debug": [myID]})
        
    async def delete_debug(self, myID):
        check = await collection.find_one({"_id": "debug"})
        if check:
            await collection.update_one({"_id": "debug"}, {"$pull": {"debug": myID}})
        else:
            return False
    
    async def get_debug_list(self):
        check = await collection.find_one({"_id": "debug"})
        if check:
            debugList = [int(debug) for debug in check["debug"]]
            return debugList
        else:
            return None


class SaveUser:
    def __init__(self) -> None:
        pass

    async def save_user(self, userID: str):
        check = await collection.find_one({"_id": "users"})
        if check:
            if userID in check["users"]:
                return None
            else:
                await collection.update_one({"_id": "users"}, {"$push": {"users": userID}})
        else:
            await collection.insert_one({"_id": "users", "users": [userID]})
        
    async def delete_user(self, userID: str):
        check = await collection.find_one({"_id": "users"})
        if check:
            await collection.update_one({"_id": "users"}, {"$pull": {"users": userID}})
        else:
            return False
    
    async def get_users(self):
        check = await collection.find_one({"_id": "users"})
        if check:
            userList = [int(user) for user in check["users"]]
            return userList
        else:
            return None

