#! python3

import math
import os
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

class Modes:
    gather = 'gather'
    sem_gather = 'sem_gather'
    chunked_gather = 'chunked_gather'
    queue = 'queue'

os.environ['RANDOM_SEED'] = RANDOM_SEED = os.environ.get('RANDOM_SEED', '4321')
os.environ['SLEEP_TIME'] = SLEEP_TIME = os.environ.get('SLEEP_TIME', '0.1')
os.environ['SLEEP_TIME_MAX'] = SLEEP_TIME_MAX = os.environ.get('SLEEP_TIME_MAX', '1')


def draw_plot(COROUTINES_COUNT, COROUTINES_LIMIT, AWAIT_COUNT, MODE):
    os.environ['COROUTINES_COUNT'] = str(COROUTINES_COUNT)
    os.environ['COROUTINES_LIMIT'] = str(COROUTINES_LIMIT)
    os.environ['AWAIT_COUNT'] = str(AWAIT_COUNT)

    raw_data = os.popen(
        'python3 -m random_ ' + MODE + ' --format {random_seed},{coroutines_count},{coroutines_limit},{await_count},{awaits_time}'
    ).read()


    data = []
    for rd in raw_data.split():
        d = rd.split(',')
        data.append((d[4], float(d[5]), float(d[6])))

    coros = sorted(set([d[0] for d in data]))
    cats = dict(zip(
        coros,
        range(len(coros)),
    ))

    verts = []

    for d in sorted(data):
        v =  [
            (d[1], cats[d[0]]-.4),  # down-left
          (d[1], cats[d[0]]+.4),  # upper-left
          (d[2], cats[d[0]]+.3),  # upper-right
          (d[2], cats[d[0]]-.3),  # down-right
        ]
        verts.append(v)

    bars = PolyCollection(verts,) 

    fig, ax = plt.subplots()
    ax.add_collection(bars)
    ax.autoscale()

    ax.set_yticks(list(range(len(coros))))
    ax.set_yticklabels(coros, rotation='vertical')
    plt.savefig(f'{MODE}-{COROUTINES_COUNT}-{COROUTINES_LIMIT}-{AWAIT_COUNT}.png')
    plt.close()
    # plt.show()

def add_plot(coroutines_count, coroutines_limit, await_count, mode, ax):
    os.environ['COROUTINES_COUNT'] = str(coroutines_count)
    os.environ['COROUTINES_LIMIT'] = str(coroutines_limit)
    os.environ['AWAIT_COUNT'] = str(await_count)

    raw_data = os.popen(
        'python3 -m random_ ' + mode + ' --format {random_seed},{coroutines_count},{coroutines_limit},{await_count},{awaits_time}'
    ).read()


    data = []
    for rd in raw_data.split():
        d = rd.split(',')
        data.append((d[4], float(d[5]), float(d[6])))

    coros = sorted(set([d[0] for d in data]))
    cats = dict(zip(
        coros,
        range(len(coros)),
    ))

    if len(data) < 300:
        verts = []

        for d in data:
            v =  [
                (cats[d[0]]-.4, d[1]),  # down-left
                (cats[d[0]]+.4, d[1]),  # upper-left
                (cats[d[0]]+.3, d[2]),  # upper-right
                (cats[d[0]]-.3, d[2]),  # down-right
            ]
            verts.append(v)
        
        ax.set_xticks(list(range(len(coros))))
        ax.set_xticklabels(coros, fontsize='xx-small',rotation='vertical')
    else: 
        coro_periods = {}

        for d in data:
            coro_periods[d[0]] = (
                min(d[1], coro_periods.get(d[0], (float('inf'),))[0]),
                max(d[2], coro_periods.get(d[0], (None, float('-inf')))[1]),
            )
        
        verts = [
            [
                (cats[d]-.4, start),  # down-left
                (cats[d]+.4, start),  # down-right
                (cats[d]+.3, end),  # upper-right
                (cats[d]-.3, end),  # upper-left
            ]
            for d, (start, end) in coro_periods.items()
        ]

    bars = PolyCollection(verts,)
    max_d = max(data, key=lambda x: x[2])

    ax.add_collection(bars)
    ax.text(0, max_d[2], str(max_d[2]))
    
    ax.autoscale()
    ax.set_title(f'{mode} coro-count:{coroutines_count} \ncoro-limit:{coroutines_limit} await-count:{await_count}', fontsize='xx-small')
    # plt.savefig(f'{mode}-{coroutines_count}-{coroutines_limit}-{await_count}.png')
    # plt.close()
    # plt.show()

if __name__ == '__main__':
    # Draw full combinations of strategies and input params

    e = lambda x: int(7*math.exp(x))  # why not?
    full_list = [
        (e(0), e(0), e(0)),
        (e(0), e(0), e(1)),
        # (e(0), e(1), e(0)),  # вырожденный случай
        (e(1), e(0), e(0)),
        (e(1), e(0), e(1)),
        (e(1), e(1), e(0)),
        # (e(0), e(1), e(2)),  # вырожденный случай
        # (e(0), e(2), e(1)),  # вырожденный случай
        (e(1), e(0), e(2)),
        # (e(1), e(2), e(0)),  # вырожденный случай
        (e(2), e(0), e(1)),
        (e(2), e(1), e(0)),
    ]

    for (cc, cl, ac) in full_list:  #(1000, 100, 300),:

        plt.figure(figsize=(27, 24))
        fig, axs = plt.subplots(ncols=4, sharey=True)
        for axe, mode in zip(axs, [Modes.gather, Modes.chunked_gather, Modes.sem_gather, Modes.queue]):
            add_plot(coroutines_count=cc, coroutines_limit=cl, await_count=ac, mode=mode, ax=axe)

        plt.savefig(f'random_/plots/9x10/{cc}-{cl}-{ac}.svg')
        # plt.show()
