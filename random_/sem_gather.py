import asyncio
import time

from typing import List
from .base import COROUTINES_LIMIT, BaseStrategy


class SemGather(BaseStrategy):
    async def gather_with_concurrency(
        self,
        *coroutines,
        limit: int = 3,
    ):
        semaphore = asyncio.Semaphore(limit)

        async def sem_coro(coro):
            async with semaphore:
                return await coro

        return await asyncio.gather(*(sem_coro(c) for c in coroutines))


    async def do(self, coro_args: List):
        started_at = time.monotonic()
        await self.gather_with_concurrency(
            *(self.sleep_coro(f"SemCoro-{i}", arg) for i, arg in enumerate(coro_args)),
            limit=COROUTINES_LIMIT,
        )
        self.total_slept_for += time.monotonic() - started_at
