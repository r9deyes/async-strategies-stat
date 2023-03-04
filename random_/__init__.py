import argparse
import asyncio
import datetime
import os
import random
import time
from typing import Any


COROUTINES_COUNT = os.environ.get('COROUTINES_COUNT', 1000)
COROUTINES_LIMIT = os.environ.get('COROUTINES_LIMIT', 100)
AWAIT_COUNT = os.environ.get('AWAIT_COUNT', 100)

RANDOM_SEED = os.environ.get('RANDOM_SEED', datetime.datetime.utcnow().timestamp())

class BaseStrategy:
    def __init__(self): 
        self.total_slept_for = 0
        self._coros_time = []

    async def sleep_coro(self, name: str, sleep_sec: float):
        started_at = time.monotonic()
        for i in range(AWAIT_COUNT):
            await asyncio.sleep(sleep_sec / AWAIT_COUNT)

        slept_for = time.monotonic() - started_at

        self._coros_time.append((slept_for,  sleep_sec))
        # print(f"{name}:{{sleep:{sleep_sec:.4f};elapsed:{slept_for:.4f};diff:{diff:.5f}}}", end="")
    
    async def do(self, coro_args: list[Any]):
        ...

    def min_coro_time(self) -> float:
        return min([t for t, _ in self._coros_time])

    def max_coro_time(self) -> float:
        return max([t for t, _ in self._coros_time])
    
    def total_diff_elapsed_time(self) -> float:
        return sum([t-st for t,st in self._coros_time]) 

    def avg_coro_time(self) -> float:
        return sum([t for t, _ in self._coros_time])/len(self._coros_time)

    def median_coro_time(self) -> float:
        return sorted([t for t, _ in self._coros_time])[len(self._coros_time)/2]


async def main(args):
    from . import gather, sem_gather, queue, chunked_gather
    strategies: dict[str, BaseStrategy] = {
        'gather': gather.SimpleGather(),
        'sem_gather': sem_gather.SemGather(),
        'chunked_gather': chunked_gather.ChunkedGather(),
        'queue': queue.Queue(),
    }
    expected_sleep_time = 0
    coro_args = []
    # Generate random timings
    random.seed(RANDOM_SEED)
    for _ in range(COROUTINES_COUNT):
        sleep_for = random.uniform(0.005, 0.5)
        expected_sleep_time += sleep_for
        coro_args.append(sleep_for)

    strategy = strategies[args.strategy]
    await strategy.do(coro_args)
    
    if args.format != '':
        format_str = '{expected_sleep_time},{total_slept_for},{min_coro_time},{max_coro_time},{avg_coro_time},{median_coro_time},{total_diff_elapsed_time}'
    # head
    print(format_str.format(
        expected_sleep_time='expected_sleep_time',
        total_slept_for='total_slept_for',
        min_coro_time='min_coro_time',
        max_coro_time='max_coro_time',
        avg_coro_time='avg_coro_time',
        median_coro_time='median_coro_time',
        total_diff_elapsed_time='total_diff_elapsed_time',
    ))
    # stats values
    print(format_str.format(
        expected_sleep_time=expected_sleep_time,
        total_slept_for=strategy.total_slept_for,
        min_coro_time=strategy.min_coro_time(),
        max_coro_time=strategy.max_coro_time(),
        avg_coro_time=strategy.avg_coro_time(),
        median_coro_time=strategy.median_coro_time(),
        total_diff_elapsed_time=strategy.total_diff_elapsed_time(),
    ))    


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('strategy', required=True, choices=('gather', 'sem_gather', 'chunked_gather', 'queue'))
    parser.add_argument('--format', help='''string to format output stats. e.g."{expected_sleep_time},
{total_slept_for}
{min_coro_time}
{max_coro_time}
{avg_coro_time}
{median_coro_time}
{total_diff_elapsed_time}" ''')
    args = parser.parse_args()

    asyncio.run(main(args))
