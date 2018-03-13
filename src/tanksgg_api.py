#!/usr/bin/python3

import json
import os
import re
from urllib.request import urlopen
from utils import *
from _consts import *

def make_tanksgg_api_request(url):
	#print(url)
	resp = urlopen(url).read().decode("utf-8")
	return json.loads(resp)

def get_version_list():
	return make_tanksgg_api_request(tgg_versions)

def get_accessory(version):
	url = tgg_accessories.format(version = version)
	return make_tanksgg_api_request(url)

def get_tank(version, tank_name):
	url = tgg_tank.format(version = version, tank = tank_name)
	return fix_json_strings(make_tanksgg_api_request(url))

def get_tanks(version):
	url = tgg_tank_list.format(version = version)
	return make_tanksgg_api_request(url)

def save_json(data, path, filename):
	f = open(os.path.join(path, filename + '.json'), 'w')
	f.write(json.dumps(data, indent = 4, sort_keys=True))
	f.close()


save_path = '../tanksgg_api_data/'
versions = get_version_list()['versions']

save_json(versions, save_path, 'versions')

for v in versions:
	print("Processing version {}".format(v[1]))
	version_id = v[0]
	version_string = re.sub("\.", "\_", version_id)
	version_path = os.path.join(save_path, version_string)
	if not os.path.exists(version_path):
		os.mkdir(version_path)

	accessories = get_accessory(version_id)
	save_json(accessories, version_path, '_accessories')

	tank_list = get_tanks(version_id)['tanks']
	save_json(tank_list, version_path, '_tanklist')
	for i, tank in enumerate(tank_list):
		if not os.path.exists(os.path.join(version_path, tank['slug']+'.json')):
			#print(os.path.join(version_path, tank['slug']))
			tank_data = get_tank(version_id, tank['slug'])
			save_json(tank_data, version_path, tank['slug'])
		update_progress(i + 1, len(tank_list))

	print()