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
os.environ['SLEEP_TIME_MAX'] = SLEEP_TIME_MAX = os.environ.get('SLEEP_TIME_MAX', '2')


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
        v =  [(d[1], cats[d[0]]-.4),  # down-left
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
    ax.set_yticklabels(coros)
    plt.savefig(f'{MODE}-{COROUTINES_COUNT}-{COROUTINES_LIMIT}-{AWAIT_COUNT}.png')
    plt.close()
    # plt.show()

if __name__ == '__main__':
    # Draw full combinations of strategies and input params
    for mode in [Modes.gather, Modes.chunked_gather, Modes.sem_gather, Modes.queue]:
        # why not?
        e = lambda x: int(7*math.exp(x))
        
        for (cc, cl, ac) in [
            (e(0), e(0), e(0)),
            (e(0), e(0), e(1)),
            (e(0), e(1), e(0)),  # вырожденный случай
            (e(1), e(0), e(0)),
            (e(1), e(0), e(1)),
            (e(1), e(1), e(0)),
            (e(0), e(1), e(2)),  # вырожденный случай
            (e(0), e(2), e(1)),  # вырожденный случай
            (e(1), e(0), e(2)),
            (e(1), e(2), e(0)),  # вырожденный случай
            (e(2), e(0), e(1)),
            (e(2), e(1), e(0)),
        ]:
            draw_plot(COROUTINES_COUNT=cc, COROUTINES_LIMIT=cl, AWAIT_COUNT=ac, MODE=mode)
