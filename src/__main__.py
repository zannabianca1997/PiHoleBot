import asyncio
import logging

from telepot.aio.loop import MessageLoop

from piholebot import PiHoleBot
from setup import token_file
from users import admins_list

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

with open(token_file) as tkn_file:
    TOKEN = tkn_file.read()

loop = asyncio.get_event_loop()  # create event loop

if len(admins_list) == 0:  # nessun admin, avvio procedura di primo setup
    from first_setup import first_setup

    loop.run_until_complete(first_setup(TOKEN))

bot = PiHoleBot(TOKEN)
loop.create_task(MessageLoop(bot).run_forever())
logger.info('Listening ...')
loop.run_forever()
