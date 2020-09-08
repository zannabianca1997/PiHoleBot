import asyncio
import logging
import os
import secrets

from telepot.aio import Bot

from setup import token_file
from users import add_user, add_admin
from users import admins_list

logger = logging.getLogger(__name__)


async def first_setup(bot):
    """Guida l'utente all'aggiunta del primo user e admin"""
    logger.info("Starting first admin confirmation")
    setup_token = secrets.token_urlsafe(5)  # 5 so it's a short string. it's single use anyway
    bot_properties = await bot.getMe()
    print(f"Please write to the bot at @{bot_properties['username']} in private chat.\n"
          f" The one time password is {setup_token}")
    new_user_id = None
    while new_user_id is None:
        for update in await bot.getUpdates(allowed_updates=["message"]):  # collect all messages
            if "message" not in update:  # sometimes some old updates can get through
                continue
            msg = update["message"]
            if "text" not in msg:  # è un messaggio ma non di testo
                continue
            if msg["text"].strip() == setup_token:
                new_user_id = msg["from"]["id"]
                await bot.sendMessage(
                    msg["chat"]["id"],
                    "Password accettata",
                    reply_to_message_id=msg["message_id"]
                )
                break  # no need to check other messages
    logger.info(f"Accepted token from {new_user_id}")
    print("Password received")
    add_user(new_user_id)
    add_admin(new_user_id)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    if os.geteuid() != 0:  # checking if i am superuser
        print("Modifing userlist need superuser privileges")
        exit(1)

    loop = asyncio.get_event_loop()  # create event loop
    with open(token_file) as tkn_file:
        TOKEN = tkn_file.read()
    bot = Bot(TOKEN)
    if len(admins_list) == 0:  # nessun admin, primo setup
        loop.run_until_complete(first_setup(bot))
    # todo: create user add/remove bot
