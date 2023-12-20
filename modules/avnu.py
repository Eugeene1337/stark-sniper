import aiohttp

from loguru import logger
from starknet_py.net.client_models import Call
from starknet_py.hash.selector import get_selector_from_name

from config import AVNU_CONTRACT, STARKNET_TOKENS
from utils.helpers import retry
from . import Starknet


async def get_quotes(from_token: int, to_token: int, amount: int):
    async with aiohttp.ClientSession() as session:
        url = "https://starknet.api.avnu.fi/swap/v1/quotes"

        params = {
            "sellTokenAddress": hex(from_token),
            "buyTokenAddress": hex(to_token),
            "sellAmount": hex(amount),
            "excludeSources": "Ekubo"
        }
        
        response = await session.get(url=url, params=params)
        response_data = await response.json()
        
        quote_id = response_data[0]["quoteId"]

        return quote_id


async def build_transaction(quote_id: str, recipient: int, slippage: float):
    async with aiohttp.ClientSession() as session:
        url = "https://starknet.api.avnu.fi/swap/v1/build"

        data = {
            "quoteId": quote_id,
            "takerAddress": hex(recipient),
            "slippage": float(slippage / 100),
        }

        response = await session.post(url=url, json=data)
        response_data = await response.json()

        return response_data


class Avnu(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str, custom_rpc: str) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account, custom_rpc=custom_rpc)

    @retry
    async def swap(
            self,
            from_token: str,
            to_token: int,
            min_amount: float,
            max_amount: float,
            decimal: int,
            slippage: float,
            all_amount: bool,
            min_percent: int,
            max_percent: int
    ):
        amount_wei, amount, balance = await self.get_amount(
            from_token,
            min_amount,
            max_amount,
            decimal,
            all_amount,
            min_percent,
            max_percent
        )

        logger.info(
            f"[{self._id}][{hex(self.address)}] Swap on Avnu - {from_token} -> {to_token} | {amount} {from_token}"
        )
        
        quote_id = await get_quotes(STARKNET_TOKENS[from_token], to_token, amount_wei)

        transaction_data = await build_transaction(quote_id, self.address, slippage)

        approve_contract = self.get_contract(STARKNET_TOKENS[from_token])

        approve_call = approve_contract.functions["approve"].prepare(
            AVNU_CONTRACT["router"],
            amount_wei
        )

        calldata = [int(i, 16) for i in transaction_data["calldata"]]

        swap_call = Call(
            to_addr=AVNU_CONTRACT["router"],
            selector=get_selector_from_name(transaction_data["entrypoint"]),
            calldata=calldata,
        )

        transaction = await self.sign_transaction([approve_call, swap_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)