#!/usr/bin/python3
import requests
from bs4 import *

r = requests.get('https://www.cricbuzz.com/cricket-match/live-scores')

s = BeautifulSoup(r.text,'html.parser')

try:
    live = s.findAll('a',attrs={'class':'cb-lv-scrs-well-live'})
except AttributeError:
    print('No LIVE cricket matches happening')
    exit()

print("LIVE CRICKET SCORES AROUND THE WORLD: \n")

for i,j in enumerate(live,1):
    print(i,' - ',j.text.lstrip())
