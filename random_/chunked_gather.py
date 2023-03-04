import asyncio
import itertools
import time

from typing import Any
from async_task_executors import COROUTINES_LIMIT

from random_ import BaseStrategy


def chunk(iterable, n):
    it = iter(iterable)
    while True:
        c = tuple(itertools.islice(it, n))
        if not c:
            return
        yield c


class ChunkedGather(BaseStrategy):
    async def do(self, coro_args: list[Any]):
        started_at = time.monotonic()
        for j, coro_args_chunk in enumerate(chunk(coro_args, COROUTINES_LIMIT)):
            await asyncio.gather(
                *(self.sleep_coro(f"Ch{j}Coro-{i}", arg) for i, arg in enumerate(coro_args_chunk))
            )
        self.total_slept_for = time.monotonic() - started_at
        # print(f'\n{COROUTINES_LIMIT} tasks slept in parallel for {total_slept_for:.4f} seconds')
