#!/usr/bin/python3
import requests
from bs4 import *

country = input("Enter the country:\n> ")
city = input(f"Enter any city in {country}:\n> ")

headers = {'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
r = requests.get(f"https://www.timeanddate.com/weather/{country}/{city}",headers=headers)
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
