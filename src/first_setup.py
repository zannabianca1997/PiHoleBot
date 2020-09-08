import logging
import secrets

from telepot.aio import Bot

from users import add_user, add_admin

logger = logging.getLogger(__name__)


async def first_setup(TOKEN):
    """Guida l'utente all'aggiunta del primo user e admin"""
    logger.info("Starting first setup procedure")
    print("Hello! The bot is without an administrator.")
    setup_token = secrets.token_urlsafe(5)  # 5 so it's a short string. it's single use anyway
    bot = Bot(TOKEN)
    bot_properties = await bot.getMe()
    print(f"Please write to the bot at @{bot_properties['username']} in private chat.\n"
          f" The one time password is {setup_token}")
    new_admin_id = None
    while new_admin_id is None:
        for update in await bot.getUpdates(allowed_updates=["message"]):  # collect all messages
            if "message" not in update:  # sometimes some old updates can get through
                continue
            msg = update["message"]
            if "text" not in msg:  # è un messaggio ma non di testo
                continue
            if msg["text"].strip() == setup_token:
                new_admin_id = msg["from"]["id"]
                await bot.sendMessage(
                    msg["chat"]["id"],
                    "Password accettata",
                    reply_to_message_id=msg["message_id"]
                )
                break  # no need to check other messages
    logger.info(f"Accepted token from {new_admin_id}")
    print("Password received")
    add_user(new_admin_id)
    add_admin(new_admin_id)
