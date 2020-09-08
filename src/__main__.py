import asyncio
import logging

from telepot.aio.loop import MessageLoop

from piholebot import PiHoleBot
from setup import token_file
from users import users_list

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

with open(token_file) as tkn_file:
    TOKEN = tkn_file.read()

loop = asyncio.get_event_loop()  # create event loop

if len(users_list) == 0:  # nessun admin, avvio procedura di primo setup
    logger.warning("Bot was launched with no user")
    print("User list is empty, use manage_user.py as root to add some")
    exit(1)

bot = PiHoleBot(TOKEN)
loop.create_task(MessageLoop(bot).run_forever())
logger.info('Listening ...')
loop.run_forever()
