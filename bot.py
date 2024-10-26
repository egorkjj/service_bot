import asyncio, logging, os
from typing import Union
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from tg_bot.config import load_config
from tg_bot.handlers import register_registration_handlers, register_user_handlers, register_admin_handlers, register_service_handlers, register_sell_handlers

storage = MemoryStorage()
logger = logging.getLogger(__name__)


class AlbumMiddleware(BaseMiddleware):
    """This middleware is for capturing media groups."""

    album_data: dict = {}

    def __init__(self, latency: Union[int, float] = 0.01):
        """
        You can provide custom latency to make sure
        albums are handled properly in highload.
        """
        self.latency = latency
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        if not message.media_group_id:
            return

        try:
            self.album_data[message.media_group_id].append(message)
            raise CancelHandler()  # Tell aiogram to cancel handler for this group element
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            message.conf["is_last"] = True
            data["album"] = self.album_data[message.media_group_id]

    async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
        """Clean up after handling our album."""
        if message.media_group_id and message.conf.get("is_last"):
            del self.album_data[message.media_group_id]


def register_all_handlers(dp):
    register_registration_handlers(dp)
    register_user_handlers(dp)
    register_admin_handlers(dp)
    register_service_handlers(dp)
    register_sell_handlers(dp)
    
async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    
    logger.info("Starting bot")
    config = load_config('.env')
    bot = Bot(token=config.tg_bot.token, parse_mode = 'HTML')
    dp = Dispatcher(bot, storage=storage) 
    bot['config'] = config
    register_all_handlers(dp)
    bot['dp'] = dp

    if not os.path.isdir('tg_bot/photos'):
        os.mkdir("tg_bot/photos")

    if not os.path.isdir('tg_bot/documents'):
        os.mkdir("tg_bot/documents")

    while True:
        try:
            dp.middleware.setup(AlbumMiddleware())
            await dp.start_polling()
        except Exception as e:
            if not isinstance(e, RuntimeError):
                print(e)


if __name__ == '__main__':
    asyncio.run(main())