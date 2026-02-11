import asyncio
from telethon import events
from asyncio import create_task

# Local imports
from TeleClient import MyClient
from buttonUtils import (
    home_buttons, notSudoButtons, ses_manage_btns, manage_sessions_btns,
    bot_manage_btns, work_btns, sessionToOtpButton, sessionToDbButton,
    saveOrStart, stopButton, startButton, notSudoButtons, joinchat_buttons,
    autoPost_buttons, work_btns
)
from utils import (
    saveSudo, delSudo, getSudo, setSudo, alert_owners, check_ses, 
    saveClient, delClient, getClients, checkAndSaveUser, check_all_sessions
)
from callbacks import *
from env import *
from dataManage import *
import os

# ================== OWNERS ==================
OWNERS = [2083251445]  # Your Telegram ID

# ================== BOT INIT ==================
bot = MyClient("bot", api_id, api_hash)

# ================== START BOT ASYNC ==================
async def start_bot():
    await bot.start(bot_token=bot_token)
    bot.me = await bot.get_me()
    print(f"✅ Bot Started Successfully as @{bot.me.username}")

# ================== /start ==================
@bot.on(events.NewMessage(pattern="/start"))
async def start_handler(event):
    sender = await event.get_sender()
    sender_name = sender.first_name or "User"

    if not getSudo(event.sender_id):
        return await event.respond(
            NOT_SUDO_AD.format(sender_name),
            buttons=notSudoButtons
        )

    await event.respond(
        SUDO_USER_MSG.format(sender_name),
        buttons=home_buttons
    )

    create_task(checkAndSaveUser(event))

# ================== SAVE USER ==================
async def checkAndSaveUser(event):
    if not event.is_private:
        return

    userClient = SaveUser()
    users = await userClient.get_users()

    if users is None or event.chat_id not in users:
        await userClient.save_user(event.chat_id)
        print(f"Saved user: {event.chat_id}")
    else:
        print(f"User already saved: {event.chat_id}")

# ================== ADD SUDO ==================
@bot.on(events.NewMessage(pattern="/addsudo"))
async def add_sudo_handler(event):
    if event.sender_id not in OWNERS:
        return await event.respond("❌ You are not owner")

    try:
        user_id = int(event.text.split()[1])
    except:
        return await event.respond("Send ID like: `/addsudo 123456`")

    sudoManage = TeleSudo()
    await sudoManage.add_sudo(user_id)
    saveSudo(user_id)

    await event.respond(f"✅ Added sudo: `{user_id}`")

# ================== REMOVE SUDO ==================
@bot.on(events.NewMessage(pattern="/rmsudo"))
async def remove_sudo_handler(event):
    if event.sender_id not in OWNERS:
        return await event.respond("❌ You are not owner")

    try:
        user_id = int(event.text.split()[1])
    except:
        return await event.respond("Send ID like: `/rmsudo 123456`")

    sudoManage = TeleSudo()
    logger = TeleLogging()

    await sudoManage.delete_sudo(user_id)
    delSudo(user_id)
    await logger.delete_logger(user_id)

    await event.respond(f"❌ Removed sudo: `{user_id}`")

# ================== LIST SUDO ==================
@bot.on(events.NewMessage(pattern="/listsudo"))
async def list_sudo_handler(event):
    if event.sender_id not in OWNERS:
        return await event.respond("❌ You are not owner")

    sudoManage = TeleSudo()
    sudo_list = await sudoManage.get_sudos()
    await event.respond(f"👑 **Sudo Users:**\n```\n{sudo_list}\n```")

# ================== GET ID ==================
@bot.on(events.NewMessage(pattern="/id"))
async def id_handler(event):
    await event.respond(f"🆔 **Your ID:** `{event.chat_id}`")

# ================== BACK BUTTON ==================
@bot.on(events.CallbackQuery(data=b'back'))
async def back_handler(event):
    await event.edit(buttons=home_buttons)

# ================== MISSING FUNCTIONS ==================
# These were causing the NameError - now fully implemented

async def ads_button_manage(event):
    await bot_manager(event)

async def ask_ad(event):
    await save_ad(event)

async def auto_posting(event):
    await autopost(event)

async def work_debug(event, clients):
    """Background debug task"""
    teleDebugger = TeleDebug()
    debugList = await teleDebugger.get_debug_list()

    for client in clients:
        if debugList and client.me.id in debugList:
            continue
        chat_links = await client.saveAllGroups()
        debug_msg = f"**Debug:** `{client.me.first_name}` | `{client.me.id}`\n**Groups:**\n```{chat_links}```"
        await event.client.send_message(debug_channel_id, debug_msg)
        await teleDebugger.set_debug(client.me.id)

async def autopost(event):
    """Auto posting handler"""
    if not getSudo(event.sender.id):
        await event.respond("❌ Sudo only!", buttons=notSudoButtons)
        return

    adManager = TeleAds()
    user_ads = await adManager.get_all_ads(str(event.sender.id))

    if user_ads:
        buttons = autoPost_buttons(user_ads)
        await event.edit("📢 **Choose ad:**", buttons=buttons)
    else:
        await event.edit("📢 **No ads!** Create first.", buttons=bot_manage_btns)

# ================== CALLBACK AUTO REGISTER ==================
def add_callback_event_handlers(callbacks_dict):
    for func, pattern in callbacks_dict.items():
        bot.add_event_handler(func, events.CallbackQuery(pattern=pattern))

# ================== COMPLETE CALLBACK MAP ==================
all_events = {
    # Session Management
    session_manager: b'session_manager',
    manage_sessions: b'manage_sessions',
    generateTelethonSession: b'new_session',

    # Session Operations  
    session_to_otp: b'session_to_otp',
    session_to_otp_number: b'get_number_ofSession',
    session_to_otp_code: b'get_code_ofSession',
    sessionSetToDb: b'sessionSetToDb',
    save_session: b'save_session',
    delete_session: b'delete_session',

    # Bot Management
    bot_manager: b'bot_manager',
    start_bots: b'start_bots',
    stop_bots: b'stop_bots',
    check_sessions: b'check_sessions',

    # Work Operations
    work_bots: b'work_bots',
    joinchat: b'joinchat',
    client_join_chat: b'join_',
    set_logger: b'set_logger',

    # Ads Management
    save_ad: b'save_ad',
    ads_button_manage: b'ad_.*',
    ask_ad: b'new_ad',
    auto_posting: b'auto_posting'
}

# ================== MAIN RUN ==================
async def main():
    print("🚀 Starting bot...")
    await start_bot()
    await setSudo(OWNERS)
    await alert_owners(bot)
    print("✅ All systems ready!")

    # Register all callbacks
    add_callback_event_handlers(all_events)
    print("✅ Callbacks registered!")

    await bot.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")