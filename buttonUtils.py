from telethon import Button

# ---------------- HOME BUTTONS ---------------- #
home_buttons = [
    [Button.inline('⚙️ Manage Bots', b'bot_manager'),
     Button.inline('🔮 Manage Sessions', b'session_manager')],
    [Button.inline('👨‍💻 Work', b'work_bots')]
]

# ---------------- SESSION MANAGEMENT ---------------- #
ses_manage_btns = [
    [Button.inline("🔮 Manage Sessions", b'manage_sessions')],
    [Button.inline('🪶 Set Logger', b'set_logger')],
    [Button.inline('⬅️ Back', b'back')]
]

# ✅ PERFECT - Exactly as requested + Save Session added
manage_sessions_btns = [
    [Button.inline('🔮 Add Account', b'new_session'),
     Button.inline('🗑️ Delete Account', b'delete_session')],
    [Button.inline('✅ Manage Account', b'check_sessions'),
     Button.inline('💾 Save Session', b'save_session')],
    [Button.inline('⬅️ Back', b'back')]
]

# ---------------- BOT MANAGEMENT ---------------- #
bot_manage_btns = [
    [Button.inline('🚀 Start Bots', b'start_bots'),
     Button.inline('🛑 Stop Bots', b'stop_bots')],
    [Button.inline('📢 Save Ad', b'save_ad')],
    [Button.inline('⬅️ Back', b'back')]
]

# ---------------- WORK BUTTONS ---------------- #
work_btns = [
    [Button.inline('⚜️ Join Chats', b'joinchat'),
     Button.inline('♦️ Auto Posting', b'auto_posting')],
    [Button.inline('⬅️ Back', b'back')]
]

# ---------------- UTILITY BUTTONS ---------------- #
saveOrStart = [
    [Button.inline('🚀 Start Bots', b'start_bots')]
]

startButton = [[Button.inline('🚀 Start Bots', b'start_bots')]]
stopButton = [[Button.inline('🛑 Stop Bots', b'stop_bots')]]

# ---------------- DYNAMIC BUTTONS ---------------- #
async def joinchat_buttons(clients):
    buttons = []
    for client in clients[:10]:  # Limiting to the first 10 clients
        try:
            me = await client.get_me()
            data = f"join_{me.id}".encode()  # Ensure data is in bytes
            buttons.append([Button.inline(f'{me.first_name[:15]}', data)])  # Truncate names if too long
        except:
            continue
    buttons.append([Button.inline('⬅️ Back', b'back')])
    return buttons

def autoPost_buttons(user_ads):
    buttons = []
    for ad_name in user_ads[:8]:  # Limiting to the first 8 ads
        data = f"ad_{ad_name}".encode()  # Ensure data is in bytes
        buttons.append([Button.inline(ad_name[:20], data)])  # Truncate ad name if too long
    buttons.append([Button.inline('⬅️ Back', b'back')])
    return buttons

# ---------------- ACCESS DENIED ---------------- #
notSudoButtons = [
    [Button.inline('🏠 Home', b'home')]
]