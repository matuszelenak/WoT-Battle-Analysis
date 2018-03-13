import os
import json
from urllib.request import urlopen


import _consts

def get_players_xvm_stats(player_ids):
    url = 'https://stat.modxvm.com/{api}/getStats/{token}/{players}'
    players = ['{}=0'.format(_id) for _id in player_ids]
    url = url.format(api = _consts.XVM_API, token = _consts.XVM_token, players = ",".join(players))

    try:
        resp = urlopen(url).read()
    except e:
        print("Error fetching XVM stats")
        print(e)
        return []

    stats = json.loads(resp.decode('utf-8'))
    if 'players' not in stats:
        print("No stats found")
        return []
    for p in stats['players']:
        p['country'] = "Unknown" if p['flag'] == None else _consts.country_translate[p['flag'].upper()]
        del(p['v'])

    return stats['players']

def get_team_xvm_stats(team):
    ids = [p['AccountDBID'] for p in team]
    return get_players_xvm_stats(ids)


def get_replay_jsons(folder_path):
    if not os.path.exists(folder_path):
        print("Invalid path for replays")
        return []
    for filename in os.listdir(folder_path):
        f = open(os.path.join(folder_path , filename), 'r')
        j = json.loads("".join(f.readlines()))
        yield j

def convert_to_time(seconds):
    return "%02d:%02d".format(int(seconds//60), int(seconds % 60))

def convert_to_seconds(time):
    h,m,s = time.split(':')
    return int(h)*60*60 + int(m)*60 + int(s)

def update_progress(progress, total):
    print("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(progress/total * 50), progress/total*100), end="", flush=True)

def to_bins(data, count, f):
    sorted_data = sorted(data, key = f)
    min_e, max_e = f(sorted_data[0]), f(sorted_data[-1])
    i_len = (max_e - min_e) / count
    l, r = min_e, min_e + i_len
    bins = [[]]
    for e in sorted_data:
        if f(e) >= l and f(e) <= r:
            bins[-1].append(e)
        else:
            bins.append([e])
            l += i_len
            r += i_len
    return bins

def fix_json_strings(j):
    if not 'tank' in j:
        return j
    for gun in j['tank']['guns']:
        gun['pitch_limits'] = json.loads(gun['pitch_limits'])
        gun['full_armor'] = json.loads(gun['full_armor'])
    for chassis in j['tank']['chassis']:
        chassis['full_armor'] = json.loads(chassis['full_armor'])
    for turret in j['tank']['turrets']:
        turret['full_armor'] = json.loads(turret['full_armor'])
    return j