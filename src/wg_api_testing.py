#!/usr/bin/python3

import json
import re
import time
import os

from _consts import *

from urllib.request import urlopen

def make_wg_api_request(url):
	resp = urlopen(url).read().decode("utf-8")
	time.sleep(0.1)
	return json.loads(resp)

def get_current_version():
	j = make_wg_api_request(url_tankopedia.format(app_id = wg_app_id))
	version_string = j['data']['game_version']
	return re.sub('\.', '_', version_string)

def get_tank_characteristics(vehicle_id):
	basic_info = make_wg_api_request(url_tank_basic.format(app_id = wg_app_id, tank_id = vehicle_id))
	modules_info = make_wg_api_request(url_tank_modules.format(app_id = wg_app_id, tank_id = vehicle_id))

def get_module_info(module_id, module_type):
	url = url_modules[module_type].format(app_id = wg_app_id, module_id = module_id)
	return make_wg_api_request(url)

game_version = get_current_version()
if not os.path.exists('../wg_api_data/{}'.format(game_version)):
	os.mkdir('../wg_api_data/{}'.format(game_version))

modules = json.loads("".join(open('../wg_api_data/{}/modules.json'.format(game_version), 'r').readlines()))
for module_id, module in modules['data'].items():
	module_info = get_module_info(module_id, module['type'])['data'][module_id]
	if module_info == None:
		continue
	module_info['type'] = module['type']
	module_info['weight'] = module['weight']
	open('../wg_api_data/{}/modules/{}.json'.format(game_version, module_id), 'w').write(json.dumps(module_info, indent=4, sort_keys=True, ensure_ascii=False))
"""
vehicles = json.loads("".join(open('../wg_api_data/{}/vehicles.json'.format(game_version), 'r').readlines()))
for vehicle_id, _ in vehicles['data'].items():
	pass
"""