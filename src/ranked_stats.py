#!/usr/bin/python3

import json
from utils import *
import re
import os
from matplotlib import pyplot as plt
import numpy as np
from datetime import datetime

def get_xp_position(j):
	player_team = str(int(j['Player']['Team']))
	xps = []
	for p in j['Team0'+player_team]:
		xps.append((p['XP']['Base'], p['Name']))
	xps.sort(reverse = True)
	#print(xps)
	return xps.index((j['Player']['XP']['Base'], j['Player']['Name']))

l = open('./data/ranked_log', 'r').readlines()
stats = {}
for line in l:
	g, h, _, _, file = line.split('\t')
	g, h = int(g), int(h)
	file = file[:-6]
	stats[file] = {'g' : g, 'h' : h}

by_rank = {}
for r in range(16):
	by_rank[r] = {'hits': 0, 'gold_hits': 0 , 'tank_list': {}, 'wn8':[]}
progression = []

credit_balance = {'actual':0, 'base' : 0, 'premium' : 0, 'reserve': 0, 'prem_reserve' : 0}
rank_rewards = [50,100,100,100,200,250,0,300,0,0,400,0,450,500,1000]
rank_rewards = [x*1000 for x in rank_rewards]
reached_rank = 0
commitment_mission_games = {}
for j in get_replay_jsons('../replay_jsons/ranked'):
	if j['IsIncomplete']:
		continue
	filename = os.path.basename(j['filename'].replace("\\","/")).split('.')[0]

	player_rank = int(j['Player']['RankedBattles']['PreBattle']['Rank'])
	player_rank_after = int(j['Player']['RankedBattles']['PostBattle']['Rank'])
	chevron_change = int(j['Player']['RankedBattles']['ChevronChange'])
	d = {'file': filename, 'dchevron' : chevron_change}
	d['rank_change']= player_rank_after - player_rank
	progression.append(d)


	by_rank[player_rank]['hits'] = by_rank[player_rank]['hits'] + stats[filename]['h']
	by_rank[player_rank]['gold_hits'] = by_rank[player_rank]['gold_hits'] + stats[filename]['g']

	#by_rank[player_rank]['wn8'] = by_rank[player_rank]['wn8'] + [p['wn8'] for p in get_team_xvm_stats(j['Team01'])+get_team_xvm_stats(j['Team01'])]

	date = datetime.strptime(j['Battle']['StartTime'], '%Y-%m-%dT%H:%M:%S')
	k = "{}_{}_{}".format(date.year, date.month, date.day)
	if k not in commitment_mission_games:
		commitment_mission_games[k] = 0

	mission = rank_rewards[player_rank_after - 1]
	rank_rewards[player_rank_after - 1] = 0
	if get_xp_position(j) < 10:
		commitment_mission_games[k] += 1
		if commitment_mission_games[k] % 7 == 0:
			print("Issuing commitment reward")
			mission += 50000

	c = j['Player']['Credits']
	costs = c['AutoRepair'] + c['AutoLoad'] + c['AutoEquip'] + mission
	credit_balance['actual'] += c['Profit'] + mission
	credit_balance['base'] += (c['Base']/(1.5 if j['Player']['IsPremium'] else 1) + costs)
	credit_balance['premium'] += (c['Base']*(1 if j['Player']['IsPremium'] else 1.5) + costs)
	credit_balance['prem_reserve'] += (c['Base']*(1 if j['Player']['IsPremium'] else 1.5) + c['PersonalReserve']*(1 if j['Player']['IsPremium'] else 1.5)+ costs)
	credit_balance['reserve'] += (c['Base']/(1.5 if j['Player']['IsPremium'] else 1) + c['PersonalReserve']/(1.5 if j['Player']['IsPremium'] else 1)+ costs)

print(credit_balance)

X,Y = [], []
for rank in range(4,15):
	if by_rank[rank]['hits'] == 0:
		continue
	avg_gold = by_rank[rank]['gold_hits'] / by_rank[rank]['hits'] * 100
	X.append(rank)
	Y.append(avg_gold)
plt.figure()
plt.ylabel("% of gold rounds")
plt.xlabel("Rank")
plt.plot(X, Y)
plt.grid()
plt.show()

total_gold, total_hits = 0, 0
for rank in range(16):
	total_gold += by_rank[rank]['gold_hits']
	total_hits += by_rank[rank]['hits']
print("Total gold usage {}%".format(total_gold/total_hits*100))

progression.sort(key = lambda x : x['file'])
total_chevrons = 0
X, Y = [], []
X_r, Y_r = [[] for _ in range(3)], [[] for _ in range(3)]
for game_no, point in enumerate(progression):
	X.append(game_no + 1)
	Y.append(total_chevrons)
	X_r[point['rank_change'] + 1].append(game_no)
	Y_r[point['rank_change'] + 1].append(total_chevrons)
	total_chevrons += point['dchevron']

plt.figure()
plt.ylabel("No. of chevrons")
plt.xlabel("Number of battles")
plt.plot(X, Y)
plt.grid()
plt.scatter(X_r[0], Y_r[0], color = 'red', label = 'rank lost')
plt.scatter(X_r[2], Y_r[2], color = 'green', label = 'rank gained')
plt.legend(loc='upper left')
plt.show()