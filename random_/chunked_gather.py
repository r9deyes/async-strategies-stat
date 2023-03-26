import asyncio
import itertools
import time

from typing import Any, List
from .base import COROUTINES_LIMIT, BaseStrategy


def chunk(iterable, n):
    it = iter(iterable)
    while True:
        c = tuple(itertools.islice(it, n))
        if not c:
            return
        yield c


class ChunkedGather(BaseStrategy):
    async def do(self, coro_args: List[Any]):
        self.init_time = time.monotonic()
        for j, coro_args_chunk in enumerate(chunk(coro_args, COROUTINES_LIMIT)):
            await asyncio.gather(
                *(self.sleep_coro(f"Ch{j}Coro-{i}", arg) for i, arg in enumerate(coro_args_chunk))
            )
        self.total_slept_for += time.monotonic() - self.init_time
