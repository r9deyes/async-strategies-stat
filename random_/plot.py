#! python3

import os
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection


os.environ['RANDOM_SEED'] = '4321'
os.environ['COROUTINES_COUNT'] = '7'
os.environ['COROUTINES_LIMIT'] = '3'
os.environ['AWAIT_COUNT'] = '4'
os.environ['SLEEP_TIME'] = '1.4'
os.environ['SLEEP_TIME_MAX'] = '20'
raw_data = os.popen('python3 -m random_ queue --format {random_seed},{coroutines_count},{coroutines_limit},{await_count},{awaits_time}'
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

for d in data:
    v =  [(d[1], cats[d[0]]-.4),  # down-left
          (d[2], cats[d[0]]+.4),  # upper-right
          (d[1], cats[d[0]]+.4),  # upper-left
          (d[2], cats[d[0]]-.4),  # down-right
          ]
    verts.append(v)

bars = PolyCollection(verts,) 

fig, ax = plt.subplots()
ax.add_collection(bars)
ax.autoscale()

ax.set_yticks(list(range(len(coros))))
ax.set_yticklabels(coros)
plt.show()