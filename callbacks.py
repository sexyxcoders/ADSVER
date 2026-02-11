import telethon
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors.rpcerrorlist import (
    PhoneCodeExpiredError, PhoneCodeInvalidError, PhoneNumberInvalidError,
    SessionPasswordNeededError, FloodWaitError, PhoneNumberBannedError
)
from env import *
from TeleClient import MyClient
from buttonUtils import *
from utils import *
from dataManage import *
import asyncio

user_tasks = {}

# Decorators
async def require_owner(func):
    async def wrapper(event, *args, **kwargs):
        if not getSudo(event.sender.id):
            return await event.respond(NOT_SUDO_AD.format(event.sender.first_name or "User"), buttons=notSudoButtons)
        return await func(event, *args, **kwargs)
    return wrapper

async def require_user(func):
    async def wrapper(event, *args, **kwargs):
        return await func(event, *args, **kwargs)
    return wrapper

# ---------------- MAIN NAVIGATION ---------------- #
@require_user
async def home(event):
    await event.edit('🏠 **Home**', buttons=home_buttons)

@require_user
async def session_manager(event):
    buttons = await manage_sessions_btns(event.sender.id)
    await event.edit('🔮 **Account Manager**', buttons=buttons)

@require_owner
async def bot_manager(event):
    await event.edit('⚙️ **Bot Manager**', buttons=bot_manage_btns)

@require_user
async def work_bots(event):
    await event.edit('👨‍💻 **Work**', buttons=work_btns)

# ---------------- SESSION MANAGEMENT ---------------- #
@require_user
async def manage_sessions(event):
    """Dynamic account manager"""
    buttons = await manage_sessions_btns(event.sender.id)
    await event.edit('🔮 **Accounts**', buttons=buttons)

@require_user
async def generateTelethonSession(event):
    """Generate & auto-save session"""
    await event.edit('🔄 **Creating account...**')

    for attempt in range(3):
        try:
            async with event.client.conversation(event.chat_id) as conv:
                await conv.send_message('📱 **Phone number:**\n`+91xxxxxxxxxx`')
                phone_resp = await conv.get_response()
                if await event.client.checkCancel(phone_resp): return

                phone = telethon.utils.parse_phone(phone_resp.text.strip())
                pending = await conv.send_message('⏳ **Code sending...**')

                client = MyClient(StringSession(), api_id, api_hash)
                await client.connect()
                await client.send_code_request(phone)
                await pending.edit('✅ **Enter OTP:**')

                code_resp = await conv.get_response()
                await client.sign_in(phone, code_resp.text.strip())
                me = await client.get_me()

                # AUTO SAVE
                session_str = client.session.save()
                session_mgr = TeleSession()
                
                if len(await session_mgr.get_sessions(event.sender.id)) >= 20:
                    await conv.send_message('❌ **Max 20 accounts!**')
                    return

                await session_mgr.add_session(event.sender.id, session_str)

                info = f"✅ **Added!**\n👤 `{me.first_name}`\n🆔 `{me.id}`"
                buttons = await manage_sessions_btns(event.sender.id)
                await conv.send_message(info, buttons=buttons, parse_mode='md')
                await client.disconnect()

                await event.delete()
                return

        except PhoneNumberInvalidError:
            await pending.edit('❌ **Invalid number!**')
            continue
        except PhoneNumberBannedError:
            await pending.edit('🚫 **Banned number!**')
            return
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
            continue
        except PhoneCodeInvalidError:
            await conv.send_message('❌ **Wrong code!**')
            continue
        except SessionPasswordNeededError:
            await conv.send_message('🔐 **2FA Password:**')
            pw_resp = await conv.get_response()
            await client.sign_in(password=pw_resp.text.strip())
            # Save logic same as above...
            return
        except Exception as e:
            if attempt == 2:
                await event.edit(f'❌ **Failed:** `{str(e)}`')

@require_user
async def delete_menu(event):
    buttons = await manage_sessions_btns(event.sender.id)
    await event.edit('🗑️ **Click account to delete:**', buttons=buttons)

@require_user
async def delete_specific_session(event):
    data = event.data.decode('utf-8')
    if data.startswith('del_'):
        idx = int(data.split('_')[1])
        session_mgr = TeleSession()
        sessions = await session_mgr.get_sessions(event.sender.id)
        
        if 0 <= idx < len(sessions):
            await session_mgr.delete_session(event.sender.id, sessions[idx])
            buttons = await manage_sessions_btns(event.sender.id)
            await event.edit(f'✅ **Account {idx+1} deleted!**', buttons=buttons)
        else:
            await event.answer('❌ **Not found!**', alert=True)

@require_user
async def check_sessions(event):
    await event.edit('🔍 **Checking...**')
    await check_all_sessions(event.sender.id, event)
    buttons = await manage_sessions_btns(event.sender.id)
    await event.edit('✅ **Done!**', buttons=buttons)

# ---------------- BOT CONTROL ---------------- #
@require_user
async def start_bots(event):
    msg = await event.edit('🚀 **Starting...**')
    
    clients = getClients(event.sender.id)
    if clients:
        await msg.edit('⚠️ **Already running!**', buttons=await manage_sessions_btns(event.sender.id))
        return

    session_mgr = TeleSession()
    sessions = await session_mgr.get_sessions(event.sender.id)
    
    if not sessions:
        buttons = await manage_sessions_btns(event.sender.id)
        await msg.edit('📭 **No accounts!**', buttons=buttons)
        return

    for session in sessions:
        try:
            client = MyClient(StringSession(session), api_id, api_hash)
            await client.start()
            saveClient(event.sender.id, client)
        except:
            continue

    await msg.edit(f'✅ **{len(getClients(event.sender.id))} started!**', buttons=work_btns)

@require_user
async def stop_bots(event):
    clients = getClients(event.sender.id)
    if not clients:
        buttons = await manage_sessions_btns(event.sender.id)
        await event.edit('📭 **Nothing running!**', buttons=buttons)
        return

    for client in list(clients):
        try:
            await client.disconnect()
            delClient(event.sender.id, client)
        except:
            pass

    buttons = await manage_sessions_btns(event.sender.id)
    await event.edit('🛑 **Stopped!**', buttons=buttons)

# ---------------- SUDO FUNCTIONS ---------------- #
@require_owner
async def set_logger(event):
    logger = TeleLogging()
    async with event.client.conversation(event.chat_id) as conv:
        await conv.send_message('📝 **Logger chat:**\n`@username` or `-100xxxxxxxx`')
        chat_resp = await conv.get_response()
        if await event.client.checkCancel(chat_resp): return
        
        await logger.set_logger(str(event.sender.id), chat_resp.text.strip())
        await conv.send_message('✅ **Logger set!**', buttons=work_btns)

@require_owner
async def save_ad(event):
    ad_mgr = TeleAds()
    async with event.client.conversation(event.chat_id) as conv:
        await conv.send_message('📢 **Ad name:**')
        name = (await conv.get_response()).text.strip()
        
        await conv.send_message('📝 **Ad message:**')
        msg = await conv.get_response()
        
        await conv.send_message('⏱️ **Delay (minutes):**')
        delay = (await conv.get_response()).text.strip()

        db_msg = await event.client.send_message(telegram_database_chat, msg)
        await event.client.send_message(
            telegram_database_chat,
            f"**{name}**\nID: `{db_msg.id}`\nDelay: `{delay}`min",
            reply_to=db_msg.id, parse_mode='md'
        )

        await ad_mgr.save_ad(event.sender.id, name, db_msg.id, delay)
        await event.respond('✅ **Ad saved!**', buttons=bot_manage_btns)

# ---------------- WORK FUNCTIONS ---------------- #
@require_owner
async def joinchat(event):
    clients = getClients(event.sender.id)
    if not clients:
        buttons = await manage_sessions_btns(event.sender.id)
        await event.edit('📭 **Start accounts first!**', buttons=buttons)
        return
    
    buttons = await joinchat_buttons(clients)
    await event.edit('🤖 **Choose bot:**', buttons=buttons)

async def client_join_chat(event):
    data = event.data.decode('utf-8')
    client_id = int(data.split('_')[1])
    clients = getClients(event.sender.id)

    target_client = next((c for c in clients if (await c.get_me()).id == client_id), None)
    if not target_client:
        await event.answer('❌ **Bot not found!**', alert=True)
        return

    async with event.client.conversation(event.chat_id) as conv:
        await conv.send_message('🔗 **Chat links:**\n`@group` or `t.me/+hash`')
        links_resp = await conv.get_response()
        links = [l.strip() for l in links_resp.text.split('\n') if l.strip()]

    me = await target_client.get_me()
    success = 0
    for link in links:
        try:
            if '+' in link:
                hash_ = link.split('+')[1]
                await target_client(ImportChatInviteRequest(hash_))
            else:
                username = link.split('@')[-1] if '@' in link else link.split('/')[-1]
                await target_client(JoinChannelRequest(username))
            success += 1
        except:
            continue

    await event.delete()
    await event.respond(f'✅ **{me.first_name}: {success}/{len(links)} joined!**', buttons=work_btns)

@require_owner
async def auto_posting(event):
    clients = getClients(event.sender.id)
    if not clients:
        buttons = await manage_sessions_btns(event.sender.id)
        await event.edit('📭 **Start accounts first!**', buttons=buttons)
        return
    await autopost(event)

@require_owner
async def autopost(event):
    ad_mgr = TeleAds()
    ads = await ad_mgr.get_all_ads(str(event.sender.id))
    
    if ads:
        buttons = autoPost_buttons(ads)
        await event.edit('📢 **Choose ad:**', buttons=buttons)
    else:
        await ask_ad(event)

@require_owner
async def ads_button_manage(event):
    data = event.data.decode('utf-8')
    ad_name = data.split('_')[1]
    
    ad_mgr = TeleAds()
    ad_data = await ad_mgr.get_ad(str(event.sender.id), ad_name)
    if not ad_data:
        await event.answer('❌ **Ad not found!**', alert=True)
        return

    ad_msg = await event.client.get_messages(telegram_database_chat, ids=ad_data["messageID"])
    
    await event.delete()
    await event.respond('🚀 **Posting started!** 🛑 **Stop anytime**', buttons=stopButton)

    clients = getClients(event.sender.id)
    tasks = [asyncio.create_task(autoPostGlobal(c, event, ad_msg.text, ad_data["sleepTime"])) 
             for c in clients]
    await asyncio.gather(*tasks, return_exceptions=True)

@require_owner
async def ask_ad(event):
    async with event.client.conversation(event.chat_id) as conv:
        await conv.send_message('📝 **Ad message:**')
        msg = await conv.get_response()
        await conv.send_message('⏱️ **Delay (minutes):**')
        delay = int((await conv.get_response()).text) * 60

    await event.delete()
    await event.respond('🚀 **Posting live ads!** 🛑 **Stop anytime**', buttons=stopButton)

    clients = getClients(event.sender.id)
    tasks = [asyncio.create_task(autoPostGlobal(c, event, msg.text, delay)) for c in clients]
    await asyncio.gather(*tasks, return_exceptions=True)

# ---------------- UTILITIES ---------------- #
async def work_debug(event, clients):
    debugger = TeleDebug()
    debug_list = await debugger.get_debug_list()
    
    for client in clients:
        if client.me.id in debug_list: continue
        try:
            groups = await client.saveAllGroups()
            await event.client.send_message(
                debug_channel_id,
                f"🔍 **{client.me.first_name}** ({client.me.id})\n```{groups}```",
                parse_mode='md'
            )
            await debugger.set_debug(client.me.id)
        except:
            continue