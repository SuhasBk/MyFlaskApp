#!/usr/bin/python3
import requests
from bs4 import *
import sys

try:
    if len(sys.argv[1:]) < 1:
        raise IndexError
    city = sys.argv[1]
except:
    city = input("Enter any city in India:\n> ")

headers = {'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
r = requests.get("https://www.timeanddate.com/weather/india/{}".format(city),headers=headers)
if r.ok:
    s = BeautifulSoup(r.text,'html.parser')
    a = s.find('div',attrs={'id':'qlook'})
    try:
        for i in list(a)[1::]:
            if i.text.count('°C') > 1:
                for j in i.text.split('°C'):
                    print(j)
            else:
                print(i.text)
    except:
        print("Bad city")
else:
    exit(f"Request error : {r.status_code}")
