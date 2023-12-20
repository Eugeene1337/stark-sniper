import asyncio
from concurrent.futures import ThreadPoolExecutor

from loguru import logger

from config import ACCOUNTS
from modules_settings import *
from settings import (
    TYPE_WALLET,
    QUANTITY_THREADS
)


def get_wallets():
    wallets = [
            {
                "id": _id,
                "key": key,
            } for _id, key in enumerate(ACCOUNTS, start=1)
        ]

    return wallets


async def run_module(module, account_id, key):
    try:
       await module(account_id, key, TYPE_WALLET)
            
    except Exception as e:
        logger.error(e)


def _async_run_module(module, account_id, key):
    asyncio.run(run_module(module, account_id, key))


def main(module):
    wallets = get_wallets()

    with ThreadPoolExecutor(max_workers=QUANTITY_THREADS) as executor:
        for _, account in enumerate(wallets, start=1):
            executor.submit(
                _async_run_module,
                module,
                account.get("id"),
                account.get("key"),
            )


if __name__ == '__main__':
    logger.add("logging.log")

    module = swap_avnu
    main(module)


