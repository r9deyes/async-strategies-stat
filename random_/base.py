import asyncio
import datetime
import os
import random
import sys
import time
from typing import Any, List, Dict

COROUTINES_COUNT = int(os.environ.get('COROUTINES_COUNT', 1000))
COROUTINES_LIMIT = int(os.environ.get('COROUTINES_LIMIT', 100))
AWAIT_COUNT = int(os.environ.get('AWAIT_COUNT', 100))
SLEEP_TIME = float(os.environ.get('SLEEP_TIME', 0.05))

RANDOM_SEED = os.environ.get('RANDOM_SEED', datetime.datetime.utcnow().timestamp())
SLEEP_TIME_MAX = float(os.environ.get('SLEEP_TIME_MAX', 0.5))


class BaseStrategy:
    """
    Base async strategy. Implement common sleep_coro function with counting
    """
    def __init__(self): 
        self.total_slept_for = 0
        self._coros_time = []

    async def sleep_coro(self, name: str, sleep_sec: float):
        started_at = time.monotonic()
        for i in range(AWAIT_COUNT):
            await asyncio.sleep(sleep_sec / AWAIT_COUNT)

        slept_for = time.monotonic() - started_at

        self._coros_time.append((slept_for,  sleep_sec))
    
    async def do(self, coro_args: List[Any]):
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
        return sorted([t for t, _ in self._coros_time])[len(self._coros_time)//2]


async def main(args):
    from . import gather, sem_gather, queue, chunked_gather
    strategies: Dict[str, BaseStrategy] = {
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
        sleep_for = random.uniform(SLEEP_TIME, SLEEP_TIME_MAX)
        expected_sleep_time += sleep_for
        coro_args.append(sleep_for)

    strategy = strategies[args.strategy]
    await strategy.do(coro_args)
    
    if not args.format:
        format_str = '{random_seed},{coroutines_count},{coroutines_limit},{await_count},{expected_sleep_time},{total_slept_for},{min_coro_time},{max_coro_time},{avg_coro_time},{median_coro_time},{total_diff_elapsed_time}'
    else:
        format_str = args.format

    # stats values
    sys.stdout.write(format_str.format(
        random_seed=RANDOM_SEED,
        coroutines_count=COROUTINES_COUNT,
        coroutines_limit=COROUTINES_LIMIT,
        await_count=AWAIT_COUNT,
        expected_sleep_time=expected_sleep_time,
        total_slept_for=strategy.total_slept_for,
        min_coro_time=strategy.min_coro_time(),
        max_coro_time=strategy.max_coro_time(),
        avg_coro_time=strategy.avg_coro_time(),
        median_coro_time=strategy.median_coro_time(),
        total_diff_elapsed_time=strategy.total_diff_elapsed_time(),
    )+"\n")


def print_head(args):
    if not args.format:
        format_str = '{random_seed},{coroutines_count},{coroutines_limit},{await_count},{expected_sleep_time},{total_slept_for},{min_coro_time},{max_coro_time},{avg_coro_time},{median_coro_time},{total_diff_elapsed_time}'
    else:
        format_str = args.format

    sys.stdout.write(format_str.format(
        random_seed='random_seed',
        coroutines_count='coroutines_count',
        coroutines_limit='coroutines_limit',
        await_count='awaitings_count',
        expected_sleep_time='expected_sleep_time',
        total_slept_for='total_slept_for',
        min_coro_time='min_coro_time',
        max_coro_time='max_coro_time',
        avg_coro_time='avg_coro_time',
        median_coro_time='median_coro_time',
        total_diff_elapsed_time='total_diff_elapsed_time',
    )+"\n")
