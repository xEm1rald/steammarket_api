from pathlib import Path
import aiofiles
import json

from loguru import logger

from .models.item import Item


class Cache:
    def __init__(self, cache_file: Path = Path(".cache", "steammarket.json")):
        self._file = cache_file
        self._insure_cache_file()

        self._cache: dict | None = None

    def _insure_cache_file(self) -> None:
        if not self._file.exists():
            self._file.parent.mkdir(parents=True, exist_ok=True)
            with self._file.open("w") as f:
                json.dump({}, f)

    async def _load_cache(self) -> None:
        async with aiofiles.open(self._file.absolute(), mode="r") as f:
            raw = await f.read()
            if not raw: raw = "{}"
            self._cache = json.loads(raw)

    async def update(self, item: Item) -> None:
        if not self._cache:
            await self._load_cache()

        push = {item.hash_name: item.model_dump()}
        async with aiofiles.open(self._file.absolute(), mode="w") as f:
            self._cache.update(push)
            await f.write(
                json.dumps(self._cache, indent=2)
            )

        logger.debug("{}: updated".format(item.hash_name))

    async def get(self, hash_name: str, fallback = None) -> Item:
        if not self._cache:
            await self._load_cache()

        item_raw = self._cache.get(hash_name)
        if not item_raw:
            return fallback

        return Item.model_validate(item_raw)
