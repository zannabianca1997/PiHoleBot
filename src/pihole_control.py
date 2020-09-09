import logging

import system_control

logger = logging.getLogger(__name__)


async def launch_command(bot, chat_id, command, args):
    return await system_control.launch_command(
        bot, chat_id,
        f"sudo pihole {command} {' '.join(args)}",
        logger
    )

