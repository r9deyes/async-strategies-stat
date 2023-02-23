import asyncio
import datetime
import itertools
import os
import random
import time

from typing import List


def chunk(iterable, n):
    it = iter(iterable)
    while True:
        c = tuple(itertools.islice(it, n))
        if not c:
            return
        yield c


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


async def do_w_chunked_gather(coro_args: List):
    started_at = time.monotonic()
    for j, coro_args_chunk in enumerate(chunk(coro_args, COROUTINES_LIMIT)):
        await asyncio.gather(
            *(sleep_coro(f"Ch{j}Coro-{i}", arg) for i, arg in enumerate(coro_args_chunk))
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
    await do_w_chunked_gather(coro_args)
    print(f'total expected sleep time: {total_sleep_time:.4f} seconds. '
          f'Avg diff: {sleep_coro.total_diff_elapsed_time/COROUTINES_COUNT:.4f}')


if __name__ == '__main__':
    asyncio.run(main())
