import logging
from typing import Union, Iterable

from telepot import message_identifier
from telepot.aio import Bot
from telepot.aio.helper import Sender, Editor

logger = logging.getLogger(__name__)


class MessageStream:
    def __init__(self, bot: Bot, chat_id: int, max_length: int = 4095, low_buffer: int = 25, high_buffer: int = 256):
        """

        :param bot: Il bot sottostante
        :param chat_id: La chat in cui lo stream viene scritto
        :param max_length: Massima lunghezza di un messaggio
        :param low_buffer: Numero di caratteri sotto il quale il buffer è considerato ancora da riempire
        :param high_buffer: Numero di caratteri oltre il quale il buffer è considerato da svuotare
        """
        assert max_length < 4096
        self.max_msg_lenght: int = max_length

        # underlying bot and chat sender
        self._bot: Bot = bot
        self._sender: Sender = Sender(bot, chat_id)

        # current message text and editor
        self._current_message_text: str = ""  # current text of the last message
        self._editor: Union[Editor, None] = None  # no last message

        # data buffer
        assert high_buffer >= low_buffer
        self._buffer: str = ""
        self.low_buffer: int = low_buffer
        self.high_buffer: int = high_buffer

        # closing
        self._is_closing: bool = False

    async def _pump(self) -> int:
        """Manda una singola richiesta al server, spedendo quanti più caratteri possibile.
        :return: Numero di caratteri mandati
        """
        # calcolo quanti caratteri posso mandare
        sending_chars = min(len(self._buffer), self.max_msg_lenght - len(self._current_message_text))

        sending_text = self._buffer[:sending_chars]  # la parte che spedisco ora
        # controllo che non sia composto solo da spaziature e/o whitespaces: telegram gli eliminerebbe
        if sending_text.strip() != "":
            if self._editor:  # abbiamo un messaggio già aperto
                new_txt = self._current_message_text + sending_text  # aggiungo l'update
                await self._editor.editMessageText(new_txt)  # edito il messaggio
                self._current_message_text = new_txt  # salvo il nuovo testo
                if len(new_txt) == self.max_msg_lenght:  # il messaggio è completo, cancello l'editor
                    self._current_message_text = ""
                    self._editor = None
            else:
                msg = await self._sender.sendMessage(sending_text)
                if sending_chars != self.max_msg_lenght:  # se non lo abbiamo riempito in un colpo solo
                    self._current_message_text = sending_text
                    self._editor = Editor(self._bot, message_identifier(msg))  # create new editor
        elif self._editor and (len(self._current_message_text) + sending_chars) != self.max_msg_lenght:
            # avremmo un update fatto solo di whitespaces, ma che non riempe il messaggio.
            # se lo mandiamo lo perderemmo e telegram si lamenterebbe. Quindi lo lasciamo in buffer
            sending_chars = 0
        self._buffer = self._buffer[sending_chars:]  # elimino i caratteri dal buffer
        return sending_chars

    def write(self, __s: str):
        """Buffera __s perchè sia spedito.
        Andrebbe usato insieme a drain:
            >> stream.write(s)
            >> await stream.drain()
        """
        if self.is_closing:
            raise IOError("The stream is closing")
        self._buffer += __s

    def writelines(self, lines: Iterable[str]):
        """Buffera un insieme di stringhe perchè sia spedito.
        Andrebbe usato insieme a drain:
            >> stream.writelines(lines)
            >> await stream.drain()
        """
        if self.is_closing:
            raise IOError("The stream is closing")
        for __s in lines:
            self._buffer += __s

    async def drain(self):
        """Se il livello del buffer è più alto di high_buffer, blocca finchè non è minore di low_buffer"""
        if not (len(self._buffer) > self.high_buffer):  # il buffer non è ancora pieno abbastanza
            return
        while len(self._buffer) > self.low_buffer:  # finchè non è abbastanza vuoto
            await self._pump()

    async def flush(self):
        """Manda tutto ciò che è possibile. Dopo la chiamata il buffer sarà vuoto o conterrà solo whitespaces che non
        riempono il messaggio corrente"""
        while await self._pump() > 0:  # finchè non può mandare più caratteri
            pass

    @property
    def is_closing(self):
        """True se lo stream si sta chiudendo o è chiuso"""
        return self._is_closing

    def close(self):
        """Chiude lo stream. Ogni successiva operazione di scrittura è bloccata"""
        self._is_closing = True

    async def wait_closed(self):
        """Attente finchè il buffer non è mandato tutto"""
        assert self.is_closing
        await self.flush()

    @staticmethod
    def can_write_eof():
        return False
