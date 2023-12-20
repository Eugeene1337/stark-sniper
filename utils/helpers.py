import asyncio
import traceback

from loguru import logger
from settings import RETRY_COUNT, SLEEP


def retry(func):
    async def wrapper(*args, **kwargs):
        retries = 0
        while retries < RETRY_COUNT:
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Error | {e} {traceback.format_exc()}")
                await asyncio.sleep(SLEEP)
                retries += 1

    return wrapper