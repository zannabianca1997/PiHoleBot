import asyncio
import logging

from telepot.aio.loop import MessageLoop

from piholebot import PiHoleBot
from setup import token_file

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

with open(token_file) as tkn_file:
    TOKEN = tkn_file.read()
bot = PiHoleBot(TOKEN)

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot).run_forever())
logger.info('Listening ...')
loop.run_forever()
