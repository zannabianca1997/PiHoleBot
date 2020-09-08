import asyncio
import logging
import os
import secrets

from telepot.aio import Bot

from setup import token_file
from users import add_user, add_admin
from users import admins_list, users_list

logger = logging.getLogger(__name__)


async def first_setup(bot):
    """Guida l'utente all'aggiunta del primo user e admin"""
    logger.info("Starting first admin confirmation")
    new_user_id = await find_user_id(bot)
    add_user(new_user_id)
    add_admin(new_user_id)
    return new_user_id


async def choose_admin(bot: Bot):
    """Ask to send a password, checks if the sender is an admin"""
    logger.info("Starting admin confirmation")
    admin_id = await find_user_id(bot)
    if admin_id not in admins_list:
        user = (await bot.getChatMember(admin_id, admin_id))["user"]
        logger.warning(f"User {user['first_name']} tried to confirm as a admin")
        print("You are not in the admin list. Please make an admin insert you in it")
        exit(1)
    return admin_id


async def find_user_id(bot):
    """Ask to send a one-time password, then return the user_id of whoever sent it"""
    setup_token = secrets.token_urlsafe(5)  # 5 so it's a short string. it's single use anyway
    bot_properties = await bot.getMe()
    print(f"Please write to the bot at @{bot_properties['username']} in private chat.\n"
          f" The one time password is {setup_token}")
    new_user_id = None
    offset = -1
    while new_user_id is None:
        for update in await bot.getUpdates(allowed_updates=["message"], offset=offset):  # collect all messages
            offset = max(update['update_id'], offset + 1)  # set new offset to ignore old messages
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
    return new_user_id


async def edit_users(bot):
    if len(admins_list) == 0:  # non c'è nessun admin
        editing_admin = await first_setup(bot)
    else:  # chiede di verificarsi
        editing_admin = await choose_admin(bot)
    user = (await bot.getChatMember(editing_admin, editing_admin))["user"]
    logger.info(f"Admin {user['first_name']} ({editing_admin}) start editing users")
    offset = -1
    while not exiting:
        await bot.sendMessage(editing_admin, "Mandami l'utente che vuoi aggiungere, /stop per uscire")
        exiting, user_given, offset = await _get_user_or_exit(bot, editing_admin, offset)
        if exiting:
            break
        if user_given in users_list:
            await bot.sendMessage(editing_admin, "Utente già presente")
        else:
            await bot.sendMessage(editing_admin, "Aggiungo l'utente alla userlist")
            add_user(user_given)


async def _get_user_or_exit(bot, editing_admin, offset):
    user_given = None
    exiting = False
    while (user_given is None) or exiting:
        for update in await bot.getUpdates(allowed_updates=["message"], offset=offset):  # collect all messages
            offset = max(update['update_id'], offset + 1)  # set new offset to ignore old messages
            if "message" not in update:  # sometimes some old updates can get through
                continue
            msg = update["message"]
            if "text" in msg and msg["text"].count("/stop") > 0:  # stop ricevuto
                exiting = True
            if "contact" in msg:
                contact = msg["contact"]
                if "user_id" not in contact:
                    await bot.sendMessage(editing_admin,
                                          "Questo contatto non è su Telegram",
                                          reply_to_message_id=msg["message_id"])
                else:
                    user_given = contact["user_id"]
    return exiting, user_given, offset


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    if os.geteuid() != 0:  # checking if i am superuser
        print("Modifing userlist need superuser privileges")
        exit(1)

    loop = asyncio.get_event_loop()  # create event loop
    with open(token_file) as tkn_file:
        TOKEN = tkn_file.read()
    bot = Bot(TOKEN)
    loop.run_until_complete(edit_users(bot))
