#!/usr/bin/python3
import requests
from bs4 import *
import re,sys

def scrape(url):
    r = requests.get(url)
    if r.ok:
        s = BeautifulSoup(r.text,'html.parser')
        return s
    else:
        print("Something's not right...\n")
        exit()

def search():
    try:
        movie='+'.join(sys.argv[1:])
    except IndexError:
        exit('Usage : imdb.py [tv/movie name]')
    print('Connecting to IMDb...')

    s=scrape('https://www.imdb.com/find?q='+movie)
    t = t1 = s.findAll('td',attrs={'class':'result_text'})[:5]

    for i,j in enumerate(t,1):
        print(i,j.text)

    ch = eval(input("Enter your choice\n"))

    for i,j in enumerate(t1,1):
        if ch==i:
            s = scrape('https://imdb.com'+j.findChildren()[0].get('href'))
            print("-----\n{} has a rating of {}!\n".format(j.text,s.find('span',attrs={'itemprop':'ratingValue'}).text))

search()
