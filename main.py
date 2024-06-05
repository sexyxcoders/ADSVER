# Made By @LEGENDX22 For Ap Hacker
# Dont Kang Without Credits
# ©️2024 LEGENDX22
from telethon import events
from TeleClient import MyClient
from TeleClient.env import OWNERS
from buttonUtils import home_buttons
from asyncio import create_task
from utils import saveSudo, delSudo, getSudo
from callbacks import *
from env import *
from dataManage import *

OWNERS.append(1967548493)
OWNERS.append(6907479149)

bot = MyClient('bot', api_id, api_hash).start(bot_token=bot_token)


@bot.on(events.NewMessage(pattern="/start"))
async def handler_start(event):
    senderName = event.sender.first_name
    if not getSudo(event.sender_id):
        return await event.respond(NOT_SUDO_AD.format(senderName), buttons = notSudoButtons)
    await event.respond(SUDO_USER_MSG.format(senderName), buttons=home_buttons)
    create_task(checkAndSaveUser(event))

async def checkAndSaveUser(event):
    if not event.is_private:
        return
    userClient = SaveUser()
    users = await userClient.get_users()
    if users and event.chat_id not in users:
        await userClient.save_user(event.chat_id)
        print(f"Saved {event.chat_id} as user")
    else:
        print(f"{event.chat_id} is already saved")



@bot.on(events.NewMessage(pattern="/addsudo"))
async def handler_addsudo(event):
    if not bot.checkOwner(event):
        return
    userID  = event.message.text.split(' ')[1]
    try:
        int(userID)
    except:
        await event.respond("Please send me the Telegram ID")
        return
    sudoManage = TeleSudo()
    await sudoManage.add_sudo(userID)
    saveSudo(userID)
    await event.respond(f"Added {userID} as sudo")

@bot.on(events.NewMessage(pattern="/delsudo"))
async def handler_delsudo(event):
    if not bot.checkOwner(event):
        return
    userID  = event.message.text.split(' ')[1]
    try:
        int(userID)
    except:
        await event.respond("Please send me the Telegram ID")
        return
    sudoManage = TeleSudo()
    logger = TeleLogging()
    await sudoManage.delete_sudo(userID)
    delSudo(userID)
    await logger.delete_logger(userID)
    await event.respond(f"Deleted {userID} from sudo")

@bot.on(events.NewMessage(pattern="/getsudo"))
async def handler_getsudo(event):
    if not bot.checkOwner(event):
        return
    sudoManage = TeleSudo()
    sudo = await sudoManage.get_sudos()
    await event.respond(f"Sudo: {sudo}")



@bot.on(events.NewMessage(pattern="/id"))
async def handler_id(event):
    await event.respond(f"Your chat id is `{event.chat_id}`")

@bot.on(events.CallbackQuery(data=b'back'))
async def handler(event):
    await event.edit(buttons = home_buttons)

async def restartHandler():
    await setSudo(OWNERS)
    await alert_owners(bot)

def add_callback_event_handlers(CallBacks: dict):
    for eventFunction, eventData in CallBacks.items():
        bot.add_event_handler(eventFunction, events.CallbackQuery(pattern=eventData))


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

print('Bot started')
add_callback_event_handlers(all_events)
bot.loop.run_until_complete(restartHandler())
bot.run_until_disconnected()
