import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher

from utils.config import BOT_KEY
from utils.logging.logger import BotLogger
from handlers import (
	start,
	profile,
    items,
    locations,
    quests
)
from handlers.pvp import pvp

from middlewares.user_ban import CheckUserWasBannedMiddleware

from utils.other.gifts import Gift

bot = Bot(token=BOT_KEY)
dp = Dispatcher()


async def bot_task(bot: bot, dp: Dispatcher):
    from utils.db.models import init_db
    await init_db()
    # await BotLogger().info('☑️ Запуск бота...', send_alert=True)

    dp.include_routers(
        start.router,
        profile.router,
        items.router,
        quests.router,

        locations.router,

        # pvp processing
        pvp.router,
    )
    dp.message.middleware(CheckUserWasBannedMiddleware())

    await BotLogger().info('✅ Бот запущен', send_alert=True)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, polling_timeout=11)


async def additional_tasks(bot, dp):
    scheduler = AsyncIOScheduler()
    # gift_sender = Gift(bot=bot, dp=dp)
    # scheduler.add_job(gift_sender.send_gift, 'interval', seconds=60)

    scheduler.start()


async def main(bot: bot, dp: Dispatcher):
    task1 = asyncio.create_task(bot_task(bot=bot, dp=dp))
    task2 = asyncio.create_task(additional_tasks(bot=bot, dp=dp))
    await asyncio.gather(task1, task2)


if __name__ == "__main__":
    try:
        asyncio.run(main(bot=bot, dp=dp))
    except asyncio.exceptions.CancelledError:
        pass