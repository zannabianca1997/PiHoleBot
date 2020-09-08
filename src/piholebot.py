import logging
from functools import wraps

import telepot
import telepot.aio

from pihole_control import launch_command
from setup import user_commands, admin_commands
from users import users_list, admins_list

logger = logging.getLogger(__name__)

class PiHoleBot(telepot.aio.Bot):
    @wraps(telepot.aio.Bot.__init__)
    def __init__(self, token, loop=None):
        super(PiHoleBot, self).__init__(token, loop)
        self.command_router = telepot.aio.helper.Router(
            telepot.routing.by_chat_command(pass_args=True),
            {
                "pihole": self.pihole_command,
                (None,): self.not_a_command,
                None: self.unknown_command
            }
        )
        self.router.routing_table["chat"] = self.command_router.route  # pass down all chat message

    async def handle(self, msg):
        if not msg["from"]["id"] in users_list:
            return  # ignore every message from non-users
        if not "text" in msg:
            return  # only accept text messages
        return await super(PiHoleBot, self).handle(msg)

    async def not_a_command(self, msg, args=[]):
        return  # all normal messages are ignored

    async def unknown_command(self, msg, args=[]):
        return await self.sendMessage(msg["chat"]["id"], "Unknown command", reply_to_message_id=msg["message_id"])

    async def pihole_command(self, msg, args=[]):
        if len(args) == 0:
            return await self.sendMessage(msg["chat"]["id"], "Utilizzo: /pihole command\n"
                                                             "Comandi disponibili:\n"
                                                             f"{user_commands}\n"
                                                             "Solo per admin:\n"
                                                             f"{admin_commands}\n"
                                                             "Vedi https://docs.pi-hole.net/core/pihole-command/ "
                                                             "per la documentazione",
                                          reply_to_message_id=msg["message_id"])
        if args[0] in user_commands:  # everybody can use it
            logger.info(f"User {msg['from']['first_name']} ({msg['from']['id']}) launch 'pihole {' '.join(args)}'")
            return await launch_command(self, msg["chat"]["id"], args[0], args[1:])
        if args[0] in admin_commands:
            if msg["from"]["id"] in admins_list:
                logger.info(f"Admin {msg['from']['first_name']} ({msg['from']['id']}) launch 'pihole {' '.join(args)}'")
                return await launch_command(self, msg["chat"]["id"], args[0], args[1:])
            else:
                return await self.sendMessage(msg["chat"]["id"], "Non sei tra gli amministratori purtroppo",
                                              reply_to_message_id=msg["message_id"])
        return await self.sendMessage(msg["chat"]["id"], f"Non riesco a riconoscere il comando '{args[0]}'",
                                      reply_to_message_id=msg["message_id"])
