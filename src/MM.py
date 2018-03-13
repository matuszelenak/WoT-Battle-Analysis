#!/usr/bin/python3

import json
import os
from matplotlib import pyplot as plt
import numpy as np

from utils import *

def make_markdown_table(data = [], col_h = [], row_h = [], title = None):
    result = []
    top_row = ("| " if not (col_h == [] or row_h == []) else "") + ("" if col_h == [] else "|" + "| ".join(col_h))
    result.append(top_row)
    table_data = [[row_l] + datarow for row_l, datarow in zip(row_h, data)]

    table_data = []
    for i, row in enumerate(data):
        table_data.append(["*{}*".format(row_h[i])] + row if len(row_h) > i else row)
    result.append("|:--:"*len(table_data[0]))
    for row in table_data:
        result.append("|" + "|".join([str(x) for x in row]))

    if title != None:
        print(title)
    print()
    for r in result:
        print(r)
    print()
    print()

def get_score(j):
    scores = [0,0]
    for i, team in enumerate(["Team01", "Team02"]):
        killed = 0
        for player in j[team]:
            if not player["IsAlive"]:
                killed += 1
        scores[(i + 1)%2] += killed
    return abs(scores[0] - scores[1])

def get_position(j):
    subject_tier = int(j['Player']['Tank']['Info']['Tier'])
    tier_list = list(set([int(p['Tank']['Info']['Tier']) for p in j['Team01']]))
    tier_list.sort(reverse = True)
    if subject_tier not in tier_list:
        return (None, None, None)
    p = tier_list.index(subject_tier)
    if p == 0:
        position = "Top tier"
    elif p == len(tier_list)//2 and len(tier_list) == 3:
        position = "Middle tier"
    else:
        position = "Bottom tier"
    if len(tier_list) == 3:
        return (subject_tier, position, "3/5/7")
    elif len(tier_list) == 2:
        return (subject_tier, position, "5/10")
    else:
        return (subject_tier, position, "15")

def get_median_xp(j):
    winner_id = j['Battle']['WinnerTeam']
    winner_xp_v = []
    for player in j['Team0'.format(winner_id)]:
        winner_xp_v.append(player['XP']['Base'])
    winner_median_xp = np.median(winner_xp_v)

    loser_xp_v = []
    for player in j['Team0'.format((winner_id + 1)%2)]:
        loser_xp_v.append(player['XP']['Base'])
    loser_median_xp = np.median(loser_xp_v)

    return (winner_median_xp, loser_median_xp)

d_map = {}
matchmaking = {}
templates = ["3/5/7", "5/10", "15"]
pref_mm_tanks = ['Panther/M10', 'StuG IV', 'T26E4 SuperPershing', 'IS-6', 'Pz.Kpfw. 38H 735 (f)', 'E 25']
to_process = 1800

game_durations, kill_differences,template_occurence = {}, {}, {}

tiers = {}
for t in range(1,11):
    tiers[t] = 0

tanks = {}

for t in templates:
    game_durations[t] = []
    kill_differences[t] = []
    template_occurence[t] = 0

for filename, done in zip(os.listdir("./replay_jsons"), range(len(list(os.listdir("./replay_jsons"))))[:to_process]):
    update_progress(done, to_process)
    f = open(os.path.join("./replay_jsons/" , filename), 'r')
    j = json.loads("".join(f.readlines()))
    if j['Player']['Tank']['Name_Tank'] in pref_mm_tanks:
        continue

    tanks[j['Player']['Tank']['Name_Tank']] = True

    f.close()

    tier, position, template = get_position(j)
    if tier == None or tier < 4:
        #print("Skipping ",filename)
        continue

    tiers[tier] = tiers[tier] + 1
    if tier not in matchmaking:
        matchmaking[tier] = []
    matchmaking[tier] = matchmaking[tier] + [(template, position)]

    template_occurence[template] = template_occurence[template] + 1

    duration = convert_to_seconds(j['Battle']['Duration'])
    game_durations[template] = game_durations[template] + [duration]

    kill_differences[template] = kill_differences[template] + [get_score(j)]

    if tier >= 5:
        map_name = j["Map"]["Name"]
        if not map_name in d_map:
            d_map[map_name] = 0
        d_map[map_name] = d_map[map_name] + 1

for t, _ in tanks.items():
    print(t)

d = []
for temp in templates:
    durs = game_durations[temp]
    kills = kill_differences[temp]
    d.append([convert_to_time(np.average(durs)), convert_to_time(np.median(durs)), np.average(kills)])

make_markdown_table(col_h = ["Time(avg)", "Time(median)", "Kill diff (avg)"], row_h = sorted(templates), data = d)
print()

for tier, results in matchmaking.items():
    positions = ['Top tier', 'Middle tier', 'Bottom tier']

    labels = positions
    sizes = [sum(x[1] == pos for x in results) for pos in labels]

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
            startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.title("Position distribution for tier {}".format(tier))

    plt.savefig('position_dist_tier{}.png'.format(tier))


    d = [[sum((x[0] == t and x[1] == pos) for x in results) for t in templates] + [sum(x[1] == pos for x in results)] for pos in positions]

    make_markdown_table(row_h = positions, col_h = templates + ['Total'], data = d, title = "Position distribution for tier {}".format(tier))

print()
for tier, results in matchmaking.items():

    labels = templates
    sizes = [sum([x[0] == temp for x in results]) for temp in templates]

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
            startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.title("Template distribution for tier {}".format(tier))

    plt.savefig('template_dist_tier{}.png'.format(tier))

    make_markdown_table(title = "Template distribution for tier {}".format(tier), row_h = templates, col_h = ["Frequency"], data = [[sum([x[0] == temp for x in results])] for temp in templates])

t = []
for mapname, count in d_map.items():
    t.append([count, mapname])

t.sort(reverse = True)

make_markdown_table(title = "Map distribution", col_h = ["Map name", "Occurence"], data = [x[::-1] for x in t])