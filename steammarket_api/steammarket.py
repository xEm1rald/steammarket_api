import aiohttp
import urllib.parse
from .enums import CurrencyCode
from .models.item import MarketPriceData, Item
from .exceptions import IncorrectHashName
from .cache import Cache
from . import utils


class Client:
    API = "https://steamcommunity.com/market"

    def __init__(self, app_id: int=730):
        self.app_id = app_id
        self.cache: Cache = Cache()

    async def _request(self, method: str, url: str, json_data: str = None) -> dict:
        async with aiohttp.request(method, url, json=json_data) as resp:
            resp.raise_for_status()
            return await resp.json()

    def _add_payload(self, url: str, payload: dict) -> str:
        return f"{url}?{'&'.join([f'{k}={urllib.parse.quote(str(v))}' for k, v in payload.items()])}"

    async def get_item_price_overview(self, market_hash_name: str, currency: CurrencyCode) -> MarketPriceData:
        resp = await self._request(
            method="GET",
            url=self._add_payload(
                url=f"{self.API}/priceoverview",
                payload={
                    'appid': self.app_id,
                    'market_hash_name': market_hash_name,
                    'currency': currency.value
                }
            )
        )

        if resp.get("lowest_price") is None:
            raise IncorrectHashName(market_hash_name, resp)

        return MarketPriceData.from_dict(resp, currency)

    async def get_item_query(self, query: str, count: int=50) -> list[Item]:
        data = await self._request(
            method="GET",
            url=self._add_payload(
                url=f"{self.API}/search/render/",
                payload={
                    'query': query,
                    'appid': self.app_id,
                    'start': 0,
                    'count': count,
                    'norender': 1
                }
            )
        )

        items = [
            Item.from_dict(item_data)
            for item_data in data.get("results")
        ]

        for item in items:
            await self.cache.update(item)

        return items

    async def get_item(self, hash_name: str, currency: CurrencyCode, market_price_data: bool = True) -> Item:
        item = await self.cache.get(hash_name)

        if not item:
            items = await self.get_item_query(hash_name, count=3)

            for item in items:
                if item.hash_name == hash_name:
                    break
            else:
                raise IncorrectHashName

        if market_price_data:
            item.market_price_data = await self.get_item_price_overview(item.hash_name, currency)

        return item