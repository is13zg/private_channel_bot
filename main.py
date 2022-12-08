import logging
from create_bot import bot, dp
from handlers import client, admin

logger = logging.getLogger(__name__)


def main() -> None:
    dp.include_router(admin.router)
    dp.include_router(client.router)
    dp.run_polling(bot)


if __name__ == "__main__":
    main()
