# utils.py - OPTIMIZED VERSION
import asyncio
import random
from telethon.errors import FloodWaitError, SessionPasswordNeededError
from telethon.sessions import StringSession
from telethon import Button
from TeleClient import MyClient
from dataManage import *
from env import *
from classUtils import FileManage

# ================= GLOBAL STATE =================
userClients = {}
SUDO_USERS = []

# ================= CLIENT STORAGE =================
def saveClient(senderID, client):
    """Save client to user storage with cleanup"""
    senderID = int(senderID)
    if senderID in userClients:
        if client not in userClients[senderID]:
            userClients[senderID].append(client)
    else:
        userClients[senderID] = [client]

def getClients(senderID):
    """Get all clients for user"""
    return userClients.get(int(senderID), [])

def delClient(senderID, client):
    """Remove specific client"""
    senderID = int(senderID)
    if senderID in userClients and client in userClients[senderID]:
        userClients[senderID].remove(client)
        if not userClients[senderID]:  # Clean empty list
            del userClients[senderID]

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
    """Check if user is sudo"""
    return int(userID) in SUDO_USERS

def getSudos():
    """Get all sudo users"""
    return SUDO_USERS.copy()

# ================= TYPE UTILS =================
def fixType(value):
    """Convert to int if possible, else str"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return str(value)

# ================= AUTO POSTING =================
async def autoPostGlobal(client, event, message, sleep_time, file=None):
    """Post message to all groups with logging"""
    sleep_time = max(int(sleep_time), 15)
    sent = []
    
    fileManager = FileManage()
    fileManager.saveFileInfo("sent.txt")
    
    logger = TeleLogging()
    loggerID = await logger.get_logger(str(event.sender.id))
    loggerID = fixType(loggerID)

    print(f"🚀 Auto posting started... ({sleep_time}s interval)")

    try:
        while True:  # Main posting loop
            dialogs = await client.get_dialogs()
            random.shuffle(dialogs)
            
            me = await client.get_me()
            myName = me.first_name or "Unknown"

            posted_count = 0
            for dialog in dialogs:
                if dialog.is_group and len(dialog.title) > 0:
                    try:
                        await client.send_message(
                            dialog.id, message, file=file
                        )
                        print(f"✅ Sent to {dialog.title} ({myName})")
                        sent.append(f"{dialog.title} ({dialog.id})")
                        posted_count += 1
                        await asyncio.sleep(random.uniform(0.5, 1.5))

                    except FloodWaitError as e:
                        print(f"⏳ FloodWait {e.seconds}s")
                        await asyncio.sleep(e.seconds)
                        continue
                    
                    except Exception as e:
                        print(f"❌ Send failed: {e}")
                        continue

            # Log results
            if posted_count > 0:
                sentList = "\n".join(sent[-50:])  # Last 50 only
                fileManager.writeFile(fileManager.file, sentList)
                
                if loggerID:
                    try:
                        await event.client.send_message(
                            loggerID,
                            f"📤 **Posted {posted_count} groups**\n👤 {myName}\n⏱️ Next: {sleep_time}s",
                            file=fileManager.file
                        )
                        fileManager.deleteFile(fileManager.file)
                    except Exception as e:
                        print(f"Logger send failed: {e}")

            sent.clear()
            await asyncio.sleep(sleep_time)

    except asyncio.CancelledError:
        print("🛑 Auto posting cancelled")
    except Exception as e:
        print(f"💥 Auto post crashed: {e}")

# ================= SESSION VALIDATION =================
async def check_ses(string, event=None):
    """Validate session string"""
    try:
        client = MyClient(StringSession(string), api_id, api_hash)
        await client.connect()
        
        if not await client.is_user_authorized():
            await client.disconnect()
            return False
            
        me = await client.get_me()
        await client.disconnect()

        # Debug log if needed
        if event and debug_channel_id:
            try:
                msg = f"✅ **Valid Session**\n👤 `{me.first_name}`\n🆔 `{me.id}`\n💾 `{string[:20]}...`"
                await event.client.send_message(debug_channel_id, msg)
            except:
                pass

        print(f"✅ Valid session: {me.first_name} ({me.id})")
        return True

    except Exception as e:
        print(f"❌ Session invalid: {e}")
        return False

async def check_all_sessions(senderID, event):
    """Clean invalid sessions for user"""
    sessionManage = TeleSession()
    all_sessions = await sessionManage.get_sessions(senderID)
    
    deleted = 0
    for session in all_sessions[:]:  # Copy to avoid modification during iteration
        if not await check_ses(session):
            await sessionManage.delete_session(senderID, session)
            deleted += 1
            await event.respond(f"🗑️ Deleted dead session #{deleted}")
        else:
            print(f"✅ Session OK: {session[:20]}...")
    
    if deleted > 0:
        await event.respond(f"✅ Cleanup complete: {deleted} dead sessions removed")

# ================= DB CLEANUP =================
async def sessionSort(senderID):
    """Remove duplicate sessions"""
    sessionManage = TeleSession()
    all_sessions = await sessionManage.get_sessions(senderID)
    unique_sessions = list(set(all_sessions))
    
    # Delete all
    for session in all_sessions:
        await sessionManage.delete_session(senderID, session)
    
    # Add unique ones back
    for session in unique_sessions:
        await sessionManage.add_session(senderID, session)
    
    print(f"✅ Deduplicated {len(unique_sessions)} sessions")
    return True

# ================= SUDO INIT =================
async def setSudo(owners_list):
    """Load all sudos from DB and memory"""
    sudoManager = TeleSudo()
    sudos = await sudoManager.get_sudos()
    
    # Load owners
    for owner_id in owners_list:
        saveSudo(owner_id)
    
    # Load DB sudos  
    for sudo_id in sudos:
        saveSudo(sudo_id)
    
    print(f"👑 Loaded {len(SUDO_USERS)} sudo users")

# ================= BOT NOTIFICATIONS =================
async def alert_owners(bot_client):
    """Notify all owners bot is ready"""
    if not hasattr(bot_client, 'me') or not bot_client.me:
        bot_client.me = await bot_client.get_me()
    
    message = (
        f"🤖 **Bot Online!**\n"
        f"👤 @{bot_client.me.username}\n"
        f"🆔 `{bot_client.me.id}`\n\n"
        f"✅ Ready for sessions & auto-posting!"
    )
    
    dmButton = [Button.url("💬 Open Bot", f"https://t.me/{bot_client.me.username}")]
    
    logger = TeleLogging()
    chats = await logger.chat_ids()
    
    sent_count = 0
    for chat_id in chats:
        try:
            chatID = fixType(chat_id)
            await bot_client.send_message(chatID, message, buttons=dmButton)
            sent_count += 1
        except Exception as e:
            print(f"Failed to notify {chatID}: {e}")
    
    print(f"📢 Alerted {sent_count} owners/channels")