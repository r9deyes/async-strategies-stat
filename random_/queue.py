import asyncio
import os
import random
import time
from datetime import datetime

from typing import Any, List

from .base import COROUTINES_LIMIT, BaseStrategy


class Queue(BaseStrategy):
    coro_count: int = 0

    async def queue_worker(self, name, queue):
        while True:
            # Get a "work item" out of the queue.
            sleep_for = await queue.get()
            self.coro_count += 1

            # Sleep for the "sleep_for" seconds.
            await self.sleep_coro(name+f'coro-{self.coro_count}', sleep_for)

            # Notify the queue that the "work item" has been processed.
            queue.task_done()



    async def do(self, coro_args: List[Any]):
        # Create a queue that we will use to store our "workload".
        queue = asyncio.Queue()

        # Put timings into the queue.
        for arg in coro_args:
            queue.put_nowait(arg)

        # Create three worker tasks to process the queue concurrently.
        tasks = []
        for i in range(COROUTINES_LIMIT):
            task = asyncio.create_task(self.queue_worker(f'worker-{i}', queue))
            tasks.append(task)

        # Wait until the queue is fully processed.
        self.init_time = time.monotonic()
        await queue.join()
        self.total_slept_for += time.monotonic() - self.init_time

        # Cancel our worker tasks.
        for task in tasks:
            task.cancel()
        # Wait until all worker tasks are cancelled.
        await asyncio.gather(*tasks, return_exceptions=True)
