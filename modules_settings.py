from modules import *


async def swap_avnu(_id, key, type_account):

    custom_rpc = ""

    # token contract
    to_token = 0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8 

    min_amount = 0.0001
    max_amount = 0.0001

    decimal = 4
    
    slippage = 1

    all_amount = False


    avnu = Avnu(_id, key, type_account, custom_rpc)
    await avnu.swap(
        "ETH", to_token, min_amount, max_amount, decimal, slippage, all_amount, 10, 10
    )
