import asyncio
import os
import random
import time
from datetime import datetime

from typing import Any

from .base import COROUTINES_LIMIT, BaseStrategy


class Queue(BaseStrategy):
    async def queue_worker(self, name, queue):
        while True:
            # Get a "work item" out of the queue.
            sleep_for = await queue.get()

            # Sleep for the "sleep_for" seconds.
            await self.sleep_coro(name, sleep_for)

            # Notify the queue that the "work item" has been processed.
            queue.task_done()



    async def do(self, coro_args: list[Any]):
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
        started_at = time.monotonic()
        await queue.join()
        self.total_slept_for = time.monotonic() - started_at

        # Cancel our worker tasks.
        for task in tasks:
            task.cancel()
        # Wait until all worker tasks are cancelled.
        await asyncio.gather(*tasks, return_exceptions=True)
