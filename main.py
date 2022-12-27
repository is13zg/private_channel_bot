import logging
from create_bot import bot, dp
from handlers import client, admin
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

logger = logging.getLogger(__name__)


async def main() -> None:
    # add interval task
    scheduler = AsyncIOScheduler()
    scheduler.add_job(admin.mails_update, trigger="interval", seconds=600)
    scheduler.start()

    dp.include_router(admin.router)
    dp.include_router(client.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
