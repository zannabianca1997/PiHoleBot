import asyncio
import logging

from telepot.aio.loop import MessageLoop

from piholebot import PiHoleBot
from setup import token_file, log_file
from users import users_list

logger = logging.getLogger(__name__)
# logging setup
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
general_log = logging.FileHandler(log_file)
general_log.setLevel(logging.INFO)
general_log.setFormatter(
    logging.Formatter('%(asctime)s:%(name)s:%(levelname)s: %(message)s')
)
root_logger.addHandler(general_log)

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
