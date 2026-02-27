import asyncio
import aiohttp
from database.models import BlacklistedAddress, async_session
from sqlalchemy import select, insert
import logging
from config import bot_config

logger = logging.getLogger(__name__)

async def fetch_blacklist_from_source(source_url: str) -> list:
    """Загружает список адресов из внешнего API"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(source_url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Предположим, что API возвращает список адресов в поле 'addresses'
                    return data.get('addresses', [])
    except Exception as e:
        logger.error(f"Error fetching blacklist from {source_url}: {e}")
    return []

async def update_blacklists():
    """Обновляет таблицу blacklisted_addresses"""
    sources = bot_config.BLACKLIST_SOURCES
    all_addresses = set()
    for source in sources:
        addresses = await fetch_blacklist_from_source(source)
        all_addresses.update(addresses)
    
    if not all_addresses:
        return
    
    async with async_session() as session:
        # Очищаем старые записи (или обновляем)
        # Для простоты удалим всё и вставим заново
        await session.execute(BlacklistedAddress.__table__.delete())
        await session.commit()
        
        # Вставляем новые
        for addr in all_addresses:
            await session.execute(
                insert(BlacklistedAddress).values(address=addr, source="external")
            )
        await session.commit()
    
    logger.info(f"Blacklist updated: {len(all_addresses)} addresses")

async def start_blacklist_updater():
    """Запускает периодическое обновление"""
    while True:
        await update_blacklists()
        await asyncio.sleep(bot_config.BLACKLIST_UPDATE_INTERVAL)
