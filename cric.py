#!/usr/bin/python3
import requests
from bs4 import *

base_url = "https://www.cricbuzz.com"
headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'}

r = requests.get(base_url+'/cricket-match/live-scores',headers=headers)

s = BeautifulSoup(r.text,'html.parser')

try:
    live = live1 = s.findAll('a',attrs={'class':'cb-lv-scrs-well-live'})
except AttributeError:
    print('No LIVE cricket matches happening')
    exit()

print("LIVE CRICKET SCORES AROUND THE WORLD: \n")

for i,j in enumerate(live,1):
    print(i,' - ',j.text.lstrip())

ch = input("\nEnter the match number\n> ")

for i,j in enumerate(live1,1):
    if ch == str(i):
        r = requests.get(base_url+j.get('href'),headers=headers)
        s = BeautifulSoup(r.text,'html.parser').find('div',attrs={'class':'cb-min-lv'})
        live = s.text.split('Recent')[0]
        a = BeautifulSoup(r.text,'html.parser').findAll('a',attrs={'class':'cb-nav-tab'})
        r = requests.get(base_url+a[1].get('href'),headers=headers)
        p = BeautifulSoup(r.text,'html.parser').findAll('div',attrs={'class':'cb-col-67'})

        print("\nMATCH INFO :\n")
        import re
        l = re.split(r'Match Info',p[0].text)
        print(l[1].replace('    ','\n').lstrip().rstrip().replace('  ',' : '))

        print("\nLIVE SCORE-CARD :\n",live)
