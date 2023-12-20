from modules import *


async def swap_avnu(_id, key, type_account):

    custom_rpc = "https://starknet-mainnet.infura.io/v3/0b09ed8b5a04445f9d8cde2629a02c9b"

    from_token = "ETH"
    to_token = "USDT"

    min_amount = 0.001
    max_amount = 0.001

    decimal = 18
    
    slippage = 30

    all_amount = False


    avnu = Avnu(_id, key, type_account, custom_rpc)
    await avnu.swap(
        from_token, to_token, min_amount, max_amount, decimal, slippage, all_amount, 10, 10
    )
