import asyncio

from aiogram import Bot
from aiogram import Dispatcher

from config import TOKEN, require_config
from handlers.start import router as start_router
from handlers.admin import router as admin_router
from handlers.profile import router as profile_router
from handlers.referrals import router as referrals_router
from handlers.my_campaigns import router as my_campaigns_router
from handlers.packages import router as packages_router
from handlers.earn import router as earn_router
from handlers.withdraw import router as withdraw_router
from handlers.support import router as support_router
from handlers.campaign_manager import router as campaign_manager_router


async def main():
    bot = Bot(token=require_config(TOKEN, "TOKEN"))
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(profile_router)
    dp.include_router(referrals_router)
    dp.include_router(my_campaigns_router)
    dp.include_router(packages_router)
    dp.include_router(earn_router)
    dp.include_router(withdraw_router)
    dp.include_router(support_router)
    dp.include_router(campaign_manager_router)

    print("Falcon Bot Started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
