import asyncio
import os
import random
import time
from datetime import datetime

from .base import BaseStrategy

class SimpleGather(BaseStrategy):

    async def do(self, coro_args):
        self.init_time = time.monotonic()
        await asyncio.gather(*(self.sleep_coro(f"GathCoro-{i}", arg) for i, arg in enumerate(coro_args)))
        self.total_slept_for += time.monotonic() - self.init_time
