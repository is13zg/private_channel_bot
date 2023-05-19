import logging
from create_bot import bot, dp
from handlers import client, admin , superadmin
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


async def main() -> None:
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(admin.update_mails_from_gk_task, trigger="interval", seconds=60)

    dt = datetime.now().replace(hour=12, minute=00, second=00)
    scheduler.add_job(admin.make_reserv_data, trigger="cron", hour=dt.hour, minute=dt.minute, start_date=datetime.now())
    scheduler.add_job(admin.command_stat, trigger="cron", hour=dt.hour, minute=dt.minute, start_date=datetime.now())
    scheduler.start()

    dp.include_router(superadmin.router)
    dp.include_router(admin.router)
    dp.include_router(client.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
