#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup
import sys,re
from fake_useragent import UserAgent

try:
    if len(sys.argv[1:]) < 1:
        raise IndexError
    city = sys.argv[1]
except:
    city = input("Enter any city in the world:\n> ")

headers = {'User-Agent':UserAgent().random}

r = requests.post("https://worldtimeserver.com/search.aspx?searchfor={}".format(city),headers=headers)
if r.ok != True:
    print(r.ok)
s = BeautifulSoup(r.text,'html.parser')

time = s.find('span',attrs={'id':'theTime'}).text.strip()
date = s.find('div',attrs={'class':'local-time'}).text.strip()
date = re.findall(r'[aA-zZ]+, [aA-zZ]+ [\d+]*, [\d+]*',date)[0]

print("TIME : {}\tDATE : {}".format(time,date))
