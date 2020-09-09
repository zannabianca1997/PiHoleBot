import asyncio
import logging

from messagestream import MessageStream

logger = logging.getLogger(__name__)


async def echo(input, output):
    """copia uno stream asincrono su un'altro stream"""
    while not input.at_eof():
        output.write(
            (await input.readline()).decode("utf-8", "backslashreplace")
        )
        await output.drain()  # drain the output


async def launch_command(bot, output_chat_id, command, error_logger: logging.Logger):
    stream = MessageStream(bot, output_chat_id)
    process = await asyncio.subprocess.create_subprocess_shell(
        command,
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )
    await echo(process.stdout, stream)
    stream.close()
    await stream.wait_closed()
