import asyncio
import os
import random
import time
from datetime import datetime

from typing import List


COROUTINES_COUNT = os.environ.get('COROUTINES_COUNT', 1000)
COROUTINES_LIMIT = os.environ.get('COROUTINES_LIMIT', 100)
AWAIT_COUNT = os.environ.get('AWAIT_COUNT', 100)

RANDOM_SEED = os.environ.get('RANDOM_SEED', datetime.datetime.utcnow().timestamp())

total_diff_elapsed_time = 0


async def sleep_coro(name, sleep_sec: int):
    started_at = time.monotonic()
    for i in range(AWAIT_COUNT):
        await asyncio.sleep(sleep_sec / AWAIT_COUNT)
    slept_for = time.monotonic() - started_at
    diff = slept_for - sleep_sec
    sleep_coro.total_diff_elapsed_time += diff
    print(f"{name}:{{sleep:{sleep_sec:.4f};elapsed:{slept_for:.4f};diff:{diff:.5f}}}", end="")


async def queue_worker(name, queue):
    while True:
        # Get a "work item" out of the queue.
        sleep_for = await queue.get()

        # Sleep for the "sleep_for" seconds.
        await sleep_coro(name, sleep_for)

        # Notify the queue that the "work item" has been processed.
        queue.task_done()

        # print(f'{name} has slept for {sleep_for:.4f} seconds')


async def work_with_queue(coro_args: List):
    # Create a queue that we will use to store our "workload".
    queue = asyncio.Queue()

    # Put timings into the queue.
    for arg in coro_args:
        queue.put_nowait(arg)

    # Create three worker tasks to process the queue concurrently.
    tasks = []
    for i in range(COROUTINES_LIMIT):
        task = asyncio.create_task(queue_worker(f'worker-{i}', queue))
        tasks.append(task)

    # Wait until the queue is fully processed.
    started_at = time.monotonic()
    await queue.join()
    total_slept_for = time.monotonic() - started_at

    # Cancel our worker tasks.
    for task in tasks:
        task.cancel()
    # Wait until all worker tasks are cancelled.
    await asyncio.gather(*tasks, return_exceptions=True)

    print(f'\n{COROUTINES_LIMIT} workers slept in parallel for {total_slept_for:.4f} seconds')


async def main():
    total_sleep_time = 0
    coro_args = []
    # Generate random timings
    random.seed(RANDOM_SEED)
    for _ in range(COROUTINES_COUNT):
        sleep_for = random.uniform(0.005, 0.5)
        total_sleep_time += sleep_for
        coro_args.append(sleep_for)

    sleep_coro.total_diff_elapsed_time = 0
    await work_with_queue(coro_args)
    print(f'total expected sleep time: {total_sleep_time:.4f} seconds. '
          f'Avg diff: {sleep_coro.total_diff_elapsed_time/COROUTINES_COUNT:.4f}')


if __name__ == '__main__':
    asyncio.run(main())
