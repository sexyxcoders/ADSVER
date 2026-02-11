from telethon import events
from asyncio import create_task

# Local imports
from TeleClient import MyClient
from buttonUtils import home_buttons, notSudoButtons
from utils import saveSudo, delSudo, getSudo
from callbacks import *
from env import *
from dataManage import *

# ================== OWNERS ==================
OWNERS = [2083251445]  # Put your Telegram ID here

# ================== START BOT ==================
bot = MyClient("bot", api_id, api_hash)
bot.start(bot_token=bot_token)

print("✅ Bot Started Successfully")

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
        return await event.respond("Send Telegram ID like: /addsudo 123456789")

    sudoManage = TeleSudo()
    await sudoManage.add_sudo(user_id)
    saveSudo(user_id)

    await event.respond(f"✅ Added sudo: {user_id}")

# ================== REMOVE SUDO ==================
@bot.on(events.NewMessage(pattern="/rmsudo"))
async def remove_sudo_handler(event):
    if event.sender_id not in OWNERS:
        return await event.respond("❌ You are not owner")

    try:
        user_id = int(event.text.split()[1])
    except:
        return await event.respond("Send Telegram ID like: /rmsudo 123456789")

    sudoManage = TeleSudo()
    logger = TeleLogging()

    await sudoManage.delete_sudo(user_id)
    delSudo(user_id)
    await logger.delete_logger(user_id)

    await event.respond(f"❌ Removed sudo: {user_id}")

# ================== LIST SUDO ==================
@bot.on(events.NewMessage(pattern="/listsudo"))
async def list_sudo_handler(event):
    if event.sender_id not in OWNERS:
        return await event.respond("❌ You are not owner")

    sudoManage = TeleSudo()
    sudo = await sudoManage.get_sudos()
    await event.respond(f"👑 Sudo Users:\n{sudo}")

# ================== GET ID ==================
@bot.on(events.NewMessage(pattern="/id"))
async def id_handler(event):
    await event.respond(f"🆔 Your ID: `{event.chat_id}`")

# ================== BACK BUTTON ==================
@bot.on(events.CallbackQuery(data=b'back'))
async def back_handler(event):
    await event.edit(buttons=home_buttons)

# ================== RESTART INIT ==================
async def restartHandler():
    await setSudo(OWNERS)
    await alert_owners(bot)

# ================== CALLBACK HANDLER AUTO REGISTER ==================
def add_callback_event_handlers(callbacks_dict):
    for func, pattern in callbacks_dict.items():
        bot.add_event_handler(func, events.CallbackQuery(pattern=pattern))

# ================== CALLBACK MAP ==================
all_events = {
    session_manager: b'session_manager',
    bot_manager: b'bot_manager',
    save_session: b'save_session',
    delete_session: b'delete_session',
    start_bots: b'start_bots',
    stop_bots: b'stop_bots',
    work_bots: b'work_bots',
    joinchat: b'joinchat',
    auto_posting: b'auto_posting',
    check_sessions: b'check_sessions',
    client_join_chat: b'join_',
    set_logger: b'set_logger',
    save_ad: b'save_ad',
    ads_button_manage: b'ad_.*',
    ask_ad: b'new_ad',
    manage_sessions: b'manage_sessions',
    generateTelethonSession: b'new_session',
    session_to_otp: b'session_to_otp',
    session_to_otp_number: b'get_number_ofSession',
    session_to_otp_code: b'get_code_ofSession',
    sessionSetToDb: b'sessionSetToDb'
}

# ================== RUN ==================
add_callback_event_handlers(all_events)
bot.loop.run_until_complete(restartHandler())
bot.run_until_disconnected()