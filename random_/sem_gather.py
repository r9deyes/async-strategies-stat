import asyncio
import datetime
import os
import random

import time

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


async def gather_with_concurrency(
    *coroutines,
    limit: int = 3,
):
    semaphore = asyncio.Semaphore(limit)

    async def sem_coro(coro):
        async with semaphore:
            return await coro

    return await asyncio.gather(*(sem_coro(c) for c in coroutines))


async def do_w_semaphored_gather(coro_args: List):
    started_at = time.monotonic()
    await gather_with_concurrency(
        *(sleep_coro(f"SemCoro-{i}", arg) for i, arg in enumerate(coro_args)),
        limit=COROUTINES_LIMIT,
    )
    total_slept_for = time.monotonic() - started_at
    print(f'\n{COROUTINES_LIMIT} tasks slept in parallel for {total_slept_for:.4f} seconds')


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
    await do_w_semaphored_gather(coro_args)
    print(f'total expected sleep time: {total_sleep_time:.4f} seconds. '
          f'Avg diff: {sleep_coro.total_diff_elapsed_time/COROUTINES_COUNT:.4f}')


if __name__ == '__main__':
    asyncio.run(main())
