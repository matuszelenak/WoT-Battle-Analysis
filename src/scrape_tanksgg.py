from bs4 import BeautifulSoup
from urllib.request import urlopen

import sys  
#from lxml import html 
from bs4 import BeautifulSoup

import re
import json
import os
import time
import requests

from PyQt5.QtCore import QEventLoop
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication


class Render(QWebEngineView):
    """Render HTML with PyQt5 WebEngine."""

    def __init__(self, html):
        self.html = None
        self.app = QApplication(sys.argv)
        QWebEngineView.__init__(self)
        self.loadFinished.connect(self._loadFinished)
        self.setHtml(html)
        while self.html is None:
            self.app.processEvents(
                QEventLoop.ExcludeUserInputEvents |
                QEventLoop.ExcludeSocketNotifiers |
                QEventLoop.WaitForMoreEvents)
        self.app.quit()

    def _callable(self, data):
        self.html = data

    def _loadFinished(self, result):
        self.page().toHtml(self._callable)


def scrape_tank_ids(tank_list_page):
    print(tank_list_page)
    tiers = tank_list_page.find_all('div', class_ = 'tier')
    r = []
    for tier in tiers:
        r += [re.search("/([^/]+)$", x['href']).group(1) for x in tier.find_all('a')]
    return r

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

def save_json(url_prefix, filename, path_prefix):
    html = urlopen(url_prefix + filename)
    soup = BeautifulSoup(html.read().decode('utf-8'), 'html.parser')
    json_string = soup.text
    fixed = fix_json_strings(json.loads(json_string))
    f = open(path_prefix + filename, 'w+')
    f.write(json.dumps(fixed, indent=4, sort_keys=True, ensure_ascii=False))
    f.close()
    return fixed    

url = 'https://tanks.gg/v10000ct/list'
source_html = requests.get(url).text

# return the JavaScript rendered HTML
rendered_html = Render(source_html).html

# get the BeautifulSoup
soup = BeautifulSoup(rendered_html, 'html.parser')
print(soup)

"""
versions = save_json("http://tanks.gg/api/", 'versions', '../tank_data/')
versions['versions'].sort(key = lambda x : x[0] + 'x')
print(versions)

renderers= []
siege_tanks = ['strv-103-0', 'strv-103b', 'udes-03', 'strv-s1']
for version in versions['versions']:

    version_id = version[0] + '/'
    print(version_id)
    if version_id == versions['current'] + '/':
        version_id = ''
    
    if not os.path.isdir('../tank_data/{0}/'.format(version_id)):
        os.mkdir('../tank_data/{0}'.format(version_id))
    #accessories
    save_json('http://tanks.gg/api/{}'.format(version_id), 'accessories', '../tank_data/{0}/'.format(version_id))

    #tanks
    url = 'http://tanks.gg/{0}list'.format(version_id)
    print(url)
    renderers.append(Render(url))
    result = renderers[-1].frame.toHtml()
    tank_list_page = BeautifulSoup(result, "html.parser")
    tank_ids = scrape_tank_ids(tank_list_page)
    for id in tank_ids:
        print(id)
        print(version_id, id)
        if os.path.isfile('../tank_data/{0}/{1}'.format(version_id, id)):
            continue
        save_json('http://tanks.gg/api/{0}tank/'.format(version_id), id, '../tank_data/{0}/'.format(version_id))
        if id in siege_tanks:
            save_json('http://tanks.gg/api/{0}tank/'.format(version_id), id + '-siege', '../tank_data/{0}/'.format(version_id))
        #time.sleep(0.1)

#curl 'http://www.wotinfo.net/en/searchfortank?tankname=strv&isCamo=true' -H 'Accept: application/js-Encoding: gzip, deflate' -H 'Accept-Language: en-US,en;q=0.5' -H 'Content-Type: application/json; charset=ISO-8859-1' -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:53.0) Gecko/20100101 Firefox/53.0'

"""