"""
run:
RANDOM_SEED=1234 python -m random_ gather
"""

import argparse
import asyncio
from . import base, gather, chunked_gather, sem_gather, queue


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('strategy', choices=('head', 'gather', 'sem_gather', 'chunked_gather', 'queue'))
    parser.add_argument('--format', help='''string to format output stats. e.g."{random_seed},
    {coroutines_count},
    {coroutines_limit},
    {await_count},
    {awaits_time},
    {expected_sleep_time},
{total_slept_for},
{min_coro_time},
{max_coro_time},
{avg_coro_time},
{median_coro_time},
{total_diff_elapsed_time}" ''')
    args = parser.parse_args()

    if args.strategy == 'head':
        base.print_head(args)
    else:
        asyncio.run(base.main(args))
