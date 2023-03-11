"""
Run scripts with countable variables to build csv file in stdout.
"""
import argparse
import os
import sys

RANGE_DEL = ':'

def split_range(arg_value, arg_name):
    try:
        if RANGE_DEL in str(arg_value):
            splited = str(arg_value).split(RANGE_DEL)
            return tuple(int(i) for i in splited)
        else:
            return int(arg_value), int(arg_value)+1

    except TypeError:
        raise TypeError(f'wrong value for {arg_name}. Use integer 100 or range 10:5000')


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('strategy', choices=('gather', 'sem_gather', 'chunked_gather', 'queue'))
    parser.add_argument('--format', help='''string to format output stats. e.g."{random_seed},{coroutines_count},{coroutines_limit},{await_count},
{expected_sleep_time},
{total_slept_for},
{min_coro_time},
{max_coro_time},
{avg_coro_time},
{median_coro_time},
{total_diff_elapsed_time}" ''')

    from base import COROUTINES_COUNT, COROUTINES_LIMIT, AWAIT_COUNT
    parser.add_argument('--coroutines-count', default=COROUTINES_COUNT)
    parser.add_argument('--coroutines-limit', default=COROUTINES_LIMIT)
    parser.add_argument('--await-count', default=AWAIT_COUNT)
    args = parser.parse_args()

    coro_count = split_range(args.coroutines_count, '--coroutines-count')
    coro_limit = split_range(args.coroutines_limit, '--coroutines-limit')
    await_count = split_range(args.await_count, '--await-count')

    format = ''
    if args.format:
        format = f'--format {args.format}'

    sys.stdout.write(
        os.popen(f'python -m random_ head {format}').read()
    )

    for c_count in range(*coro_count):
        os.putenv('COROUTINES_COUNT', str(c_count))
        for c_limit in range(*coro_limit):
            os.putenv('COROUTINES_LIMIT', str(c_limit))
            for a_count in range(*await_count):
                os.putenv('AWAIT_COUNT', str(a_count))
                sys.stdout.write(
                    os.popen(f'python -m random_ {args.strategy} {format}').read()
                )
