#!/usr/bin/python3

from urllib.request import urlopen
import json
import os
import numpy as np
from matplotlib import pyplot as plt
import sqlite3

from utils import *

def process_replays(folder_path):
    by_country = {}
    player_db = set()
    for j in get_replay_jsons(folder_path):

        try:
            p_ids = [p['AccountDBID'] for p in j['Team01'] + j['Team02']]
            r = get_players_xvm_stats(p_ids)
        except e:
            print(e)
            print(filename)
            continue

        for p in r:
            p['region'] = j['Server']
            if p['country'] not in by_country:
                by_country[p['country']] = []
            if p['_id'] not in player_db:
                player_db.add(p['_id'])
                by_country[p['country']] = by_country[p['country']] + [p]

    return by_country

#by_country = process_replays('../replay_jsons')

by_country = json.loads("".join(open('results.json', 'r').readlines()))

f = open('results.json', 'w')
f.write(json.dumps(by_country, indent=4, sort_keys=True, ensure_ascii=False))
f.close()

total_players = 0
stats = []
for country, players in by_country.items():
    corrected = [p for p in players if p['region'][:6] == 'WOT EU' and p['b'] > 0]
    if len(corrected) < 50:
        continue
    country_avg_wn8 = np.average([p['wn8'] for p in corrected])
    country_avg_wr = np.average([p['w'] / p['b'] * 100 if p['b'] > 0 else 1 for p in corrected])
    stats.append([int(country_avg_wr), int(country_avg_wn8), country, len(corrected)])
    total_players += len(players)


stats.sort(reverse = True, key = lambda x : x[-1])
topN = stats[:30]
topN.sort(reverse = True)

for stat in topN:
    print("{} WN8: {} WR : {} ({} players)".format(stat[-2], stat[1], stat[0], stat[-1]))

data = []
for country, players in by_country.items():
    corrected = [p for p in players if p['region'][:6] == 'WOT EU' and p['b'] > 0]
    if country == 'Unknown':
        continue
    data.append((len(corrected), country, corrected))

data.sort(reverse = True)

plt.figure()
plt.ylabel("WN8")
plt.xlabel("Number of battles")
for l, c, players in data[:5]:
    bins = to_bins(players, 15, lambda x : x['b'])
    bins = [b for b in bins if len(b) > 10]
    bins_avg_b = [np.average([p['b'] for p in _bin]) for _bin in bins]
    bins_avg_wn8 = [np.average([p['wn8'] for p in _bin]) for _bin in bins]
    plt.plot(bins_avg_b, bins_avg_wn8, label = str(c))
    print(c)
plt.legend(loc='upper left')
plt.show()

plt.figure()
plt.ylabel("WN8")
plt.xlabel("Average tier")
for l, c, players in data[:5]:
    bins = to_bins(players, 10, lambda x : x['lvl'])
    bins = [b for b in bins if len(b) > 10]
    bins_avg_lvl = [np.average([p['lvl'] for p in _bin]) for _bin in bins]
    bins_avg_wn8 = [np.average([p['wn8'] for p in _bin]) for _bin in bins]
    plt.plot(bins_avg_lvl, bins_avg_wn8, label = str(c))
    print(c)
plt.legend(loc='upper left')
plt.show()

avg_battles = []
for _, players in by_country.items():
    avg_battles = avg_battles + [p['b'] for p in players]

print("Player has average {} median {} battles".format(int(np.average(avg_battles)), np.median(avg_battles)))