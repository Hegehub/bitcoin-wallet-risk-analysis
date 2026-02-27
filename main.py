import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

import sentry_sdk

from config import bot_config, security_config
from core.bot import setup_bot
from core.dispatcher import setup_dispatcher
from core.middleware import setup_middleware
from core.i18n_middleware import I18nMiddleware
from database.models import init_db, create_tables
from database.redis_cache import redis_cache
from security.monitoring import SecurityMonitoring
from utils.metrics import setup_metrics, start_metrics_server
from services.update_blacklists import start_blacklist_updater

# Инициализация Sentry
if bot_config.SENTRY_DSN:
    sentry_sdk.init(
        dsn=bot_config.SENTRY_DSN,
        traces_sample_rate=1.0,
        environment="production"
    )

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def on_startup(bot: Bot, base_url: str):
    """Действия при старте бота (установка вебхука)"""
    if bot_config.USE_WEBHOOK:
        webhook_url = f"{base_url}{bot_config.WEBHOOK_PATH}"
        await bot.set_webhook(
            url=webhook_url,
            secret_token=bot_config.WEBHOOK_SECRET,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True
        )
        logger.info(f"Webhook set to {webhook_url}")

async def on_shutdown(bot: Bot):
    """Действия при остановке"""
    if bot_config.USE_WEBHOOK:
        await bot.delete_webhook()
    await bot.session.close()

async def main():
    # ... инициализация Redis, БД, метрик, как ранее ...
    
    storage = RedisStorage.from_url(bot_config.REDIS_URL)
    bot = Bot(
        token=bot_config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)
    
    # Устанавливаем i18n middleware
    i18n_middleware = I18nMiddleware()
    dp.message.middleware(i18n_middleware)
    dp.callback_query.middleware(i18n_middleware)
    
    # Остальные middleware
    await setup_middleware(dp)
    await setup_dispatcher(dp, bot, bot_config.ADMIN_IDS)
    
    # Запуск мониторинга и фоновых задач
    security_monitor = SecurityMonitoring(bot)
    asyncio.create_task(security_monitor.collect_periodically())
    
    # Запуск обновления чёрных списков
    asyncio.create_task(start_blacklist_updater())
    
    # Запуск сервера метрик Prometheus
    asyncio.create_task(start_metrics_server())
    
    if bot_config.USE_WEBHOOK:
        # Запуск aiohttp приложения для вебхуков
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=bot_config.WEBHOOK_SECRET,
        )
        webhook_requests_handler.register(app, path=bot_config.WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host=bot_config.WEBHOOK_HOST, port=bot_config.WEBHOOK_PORT)
        await site.start()
        
        # Установка вебхука после запуска сервера
        await on_startup(bot, f"https://{bot_config.WEBHOOK_HOST}:{bot_config.WEBHOOK_PORT}")
        
        logger.info(f"Webhook server started on {bot_config.WEBHOOK_HOST}:{bot_config.WEBHOOK_PORT}")
        # Бесконечное ожидание
        await asyncio.Event().wait()
    else:
        # Polling
        await on_startup(bot, "")  # без вебхука
        await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception("Fatal error")
        if bot_config.SENTRY_DSN:
            sentry_sdk.capture_exception(e)
        sys.exit(1)
