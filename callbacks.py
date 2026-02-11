import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession
from env import api_id, api_hash, bot_token, OWNERS, debug_channel_id
from TeleClient import MyClient
from buttonUtils import home_buttons, notSudoButtons
from utils import setSudo, getSudo, alert_owners
from callbacks import *
from dataManage import saveSudo, delSudo, getClients, saveClient, delClient, TeleSession, TeleLogging, TeleAds
import logging

# ================== BOT INIT ==================
bot = MyClient("bot", api_id, api_hash)

# Set up basic logging
logging.basicConfig(level=logging.INFO)

# ================== START BOT ==================
async def start_bot():
    """Start the bot and authenticate it with Telegram."""
    await bot.start(bot_token=bot_token)
    bot.me = await bot.get_me()
    logging.info(f"✅ Bot started successfully as @{bot.me.username}")

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

    # Save user in the database if not already saved
    await checkAndSaveUser(event)

# ================== ADD SUDO ==================
@bot.on(events.NewMessage(pattern="/addsudo"))
async def add_sudo_handler(event):
    """Add a user as a sudo user."""
    if event.sender_id not in OWNERS:
        return await event.respond("❌ You are not the owner")

    try:
        user_id = int(event.text.split()[1])
    except:
        return await event.respond("Send ID like: `/addsudo 123456`")

    await saveSudo(user_id)
    await event.respond(f"✅ Added sudo: `{user_id}`")

# ================== REMOVE SUDO ==================
@bot.on(events.NewMessage(pattern="/rmsudo"))
async def remove_sudo_handler(event):
    """Remove a user from the sudo list."""
    if event.sender_id not in OWNERS:
        return await event.respond("❌ You are not the owner")

    try:
        user_id = int(event.text.split()[1])
    except:
        return await event.respond("Send ID like: `/rmsudo 123456`")

    await delSudo(user_id)
    await event.respond(f"❌ Removed sudo: `{user_id}`")

# ================== LIST SUDO ==================
@bot.on(events.NewMessage(pattern="/listsudo"))
async def list_sudo_handler(event):
    """List all sudo users."""
    if event.sender_id not in OWNERS:
        return await event.respond("❌ You are not the owner")

    sudo_list = await getSudo()
    await event.respond(f"👑 **Sudo Users:**\n```\n{sudo_list}\n```")

# ================== MAIN RUN ==================
async def main():
    """Main function to start the bot and register callbacks."""
    try:
        # Start the bot
        logging.info("🚀 Starting bot...")
        await start_bot()

        # Set up sudo users
        await setSudo(OWNERS)

        # Alert owners when the bot is ready
        await alert_owners(bot)

        logging.info("✅ All systems are ready!")

        # Register callback events for all commands
        add_callback_event_handlers({
            'home': b'home',
            'session_manager': b'session_manager',
            'bot_manager': b'bot_manager',
            'work_bots': b'work_bots',
            'manage_sessions': b'manage_sessions',
            'generateTelethonSession': b'new_session',
            'delete_menu': b'delete_menu',
            'delete_specific_session': b'del_',
            'check_sessions': b'check_sessions',
            'start_bots': b'start_bots',
            'stop_bots': b'stop_bots',
            'set_logger': b'set_logger',
            'save_ad': b'save_ad',
            'joinchat': b'joinchat',
            'auto_posting': b'auto_posting',
            'ask_ad': b'new_ad'
        })

        logging.info("✅ Callbacks registered!")

        # Keep the bot running until manually stopped
        await bot.run_until_disconnected()

    except KeyboardInterrupt:
        logging.info("\n👋 Bot stopped by user.")
    except Exception as e:
        logging.error(f"❌ Fatal error: {str(e)}")
        # Optionally log to a file or report to the owner
        # logging.exception(e)

# ================== EXECUTION ==================
if __name__ == "__main__":
    # Running the main bot function
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"❌ Failed to start bot: {e}")