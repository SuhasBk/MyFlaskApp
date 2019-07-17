#!/usr/bin/python3
import requests
from bs4 import *

base_url = "https://www.cricbuzz.com"
headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'}

r = requests.get(base_url+'/cricket-match/live-scores',headers=headers)

s = BeautifulSoup(r.text,'html.parser')

try:
    live = s.findAll('a',attrs={'class':'cb-lv-scrs-well-live'})
except AttributeError:
    print('No LIVE cricket matches happening')
    exit()
print(str(len(live)))
for i,j in enumerate(live,1):
    print(i,' - ',j.text.lstrip())
