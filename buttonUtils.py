from telethon import Button

home_buttons = [
    [Button.inline('ᴍᴀɴᴀɢᴇ ʙᴏᴛꜱ ⚙️', b'bot_manager'), Button.inline(
        'ᴍᴀɴᴀɢᴇ ꜱᴇꜱꜱɪᴏɴꜱ 🔮', b'session_manager')],
    [Button.inline('ᴡᴏʀᴋ 👨‍💻', b'work_bots')]
]

ses_manage_btns = [
    [Button.inline("ᴍᴀɴᴀɢᴇ ꜱᴇꜱꜱɪᴏɴꜱ 🔮", b'manage_sessions')],
    [Button.inline('ꜱᴇᴛ ʟᴏɢɢᴇʀ 🪬', b'set_logger')],
    [Button.inline('ʙᴀᴄᴋ ⬅️', b'back')]
]

manage_sessions_btns = [
    [Button.inline('ɢᴇɴᴇʀᴀᴛᴇ ꜱᴇꜱꜱɪᴏɴ 🔮', b'new_session'), Button.inline("ꜱᴇꜱꜱɪᴏɴ ᴛᴏ ᴏᴛᴘ 💢", b"session_to_otp")],
    [Button.inline('ꜱᴀᴠᴇ ꜱᴇꜱꜱɪᴏɴ 🔮', b'save_session'), Button.inline('ᴅᴇʟᴇᴛᴇ ꜱᴇꜱꜱɪᴏɴ 🔮', b'delete_session')],
    [Button.inline("ᴄʜᴇᴄᴋ ꜱᴇꜱꜱɪᴏɴ 🔮", b'check_sessions'),Button.inline('ʙᴀᴄᴋ ⬅️', b'back')]
]

bot_manage_btns = [
    [Button.inline('ꜱᴛᴀʀᴛ ʙᴏᴛꜱ 🤖', b'start_bots'),
     Button.inline('ꜱᴛᴏᴘ ʙᴏᴛꜱ 🤖', b'stop_bots')],
     [Button.inline('ꜱᴀᴠᴇ ᴀᴅ 💼', b'save_ad'), Button.inline(
        'ᴅᴇʟᴇᴛᴇ ᴀᴅ 💼', b'delete_ad')],
    [Button.inline('ʙᴀᴄᴋ ⬅️', b'back')]
]

work_btns = [
    [Button.inline("ᴊᴏɪɴ ᴄʜᴀᴛꜱ ⚜️", b'joinchat'), Button.inline(
        "ᴀᴜᴛᴏ ᴘᴏꜱᴛɪɴɢ ♦️", b'auto_posting')],
    [Button.inline('ʙᴀᴄᴋ ⬅️', b'back')]
]


async def joinchat_buttons(clients):
    buttons = []
    for client in clients:
        client_entity = await client.get_me()
        buttons.append(
            [Button.inline(f'{client_entity.first_name} ⏩',
                           f'join_{client_entity.id}')]
        )
    buttons.append([Button.inline('ʙᴀᴄᴋ ⬅️', b'back')])
    return buttons

def autoPost_buttons(user_ads):
    buttons = []
    for ad in user_ads:
        buttons.append([Button.inline(ad, f'ad_{ad}')])
    buttons.append([Button.inline('ɴᴇᴡ ᴀᴅ 💼', 'new_ad'), Button.inline('ʙᴀᴄᴋ ⬅️', b'back')])
    return buttons
    

saveOrStart = [Button.inline('ꜱᴀᴠᴇ ꜱᴇꜱꜱɪᴏɴ 🔮', b'save_session'),
               Button.inline('ꜱᴛᴀʀᴛ ʙᴏᴛꜱ 🤖', b'start_bots')]

stopButton = [
    [Button.inline('ꜱᴛᴏᴘ ʙᴏᴛꜱ 🤖', b'stop_bots')]
]
startButton = [
    [Button.inline('ꜱᴛᴀʀᴛ ʙᴏᴛꜱ 🤖', b'start_bots')]
]

sessionToDbButton = [
    [Button.inline('ꜱᴀᴠᴇ ᴛᴏ ᴅʙ 🚀', b'sessionSetToDb'), Button.inline('ɴᴇᴡ ꜱᴇꜱꜱɪᴏɴ 🔮', b'new_session')],
    [Button.inline('ʙᴀᴄᴋ ⬅️', b'back')]
]

sessionToOtpButton = [
    [Button.inline("ɢᴇᴛ ɴᴜᴍʙᴇʀ 📩", b'get_number_ofSession') , Button.inline("ɢᴇᴛ ᴏᴛᴘ 📨", b'get_code_ofSession')],
    [Button.inline('Back', b'back')]
]

notSudoButtons = [
    Button.url("ᴛᴜᴛᴏʀɪᴀʟ ⚜️", "https://youtu.be/dxes9q4e6WQ"),
    Button.url("ᴅᴍ ᴍᴇ 📩", "https://t.me/APHACKAR"),
]