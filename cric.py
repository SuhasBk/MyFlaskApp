#!/usr/bin/python3
import requests
from bs4 import *

base_url = "https://www.cricbuzz.com"
headers = {'User-Agent':'pls let me in :('}

r = requests.get(base_url+'/cricket-match/live-scores',headers=headers)
if 'permission' in r.text.lower():
    print(r.text)
s = BeautifulSoup(r.text,'html.parser')

try:
    live = s.findAll('a',attrs={'class':'cb-lv-scrs-well-live'})
except AttributeError:
    print('No LIVE cricket matches happening')
    exit()

for i,j in enumerate(live,1):
    print(i,' - ',j.text.lstrip())
