from datetime import datetime
from pydantic import BaseModel, Field

from .. import utils
from ..enums import CurrencyCode
from ..exceptions import ParseError


class MarketPriceData(BaseModel):
    currency: CurrencyCode
    lowest_price: float
    volume: int
    median_price: float
    created_at: datetime = Field(default_factory=datetime.now)

    @staticmethod
    def from_dict(data: dict, currency: CurrencyCode) -> "MarketPriceData":
        """
        :raises ParseError
        """
        try:
            return MarketPriceData(
                currency=currency,
                lowest_price=utils.parse_price(data.get("lowest_price")),
                volume=data.get("volume", 0),
                median_price=utils.parse_price(data.get("median_price", data.get("lowest_price")))
            )
        except Exception as e:
            raise ParseError(e)


class Item(BaseModel):
    """
    It uses on searching item on market
    """
    hash_name: str
    sell_listings: int
    sell_price: int
    sell_price_text: str
    app_name: str
    app_id: int
    icon_url: str
    market_price_data: MarketPriceData | None = None

    @staticmethod
    def from_dict(data: dict) -> "Item":
        """
        :raises ParseError
        """
        try:
            return Item(
                hash_name=data.get("hash_name"),
                sell_listings=data.get("sell_listings"),
                sell_price=data.get("sell_price"),
                sell_price_text=data.get("sell_price_text"),
                app_name=data.get("app_name"),
                app_id=data.get("asset_description", {}).get("appid"),
                icon_url="https://community.fastly.steamstatic.com/economy/image/{}".format(
                    data.get("asset_description", {}).get("icon_url")
                )
            )
        except Exception as e:
            raise ParseError(e)