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
        if len(sys.argv[1:]) < 1:
            raise IndexError
        movie='+'.join(sys.argv[1:])
    except IndexError:
        movie = '+'.join(input("Enter the movie name\n").split())
    print('Connecting to IMDb...')

    s=scrape('https://www.imdb.com/find?q='+movie)
    t = t1 = s.findAll('td',attrs={'class':'result_text'})[:5]

    for i,j in enumerate(t,1):
        print(i,j.text)

    ch = eval(input("Enter your choice\n"))

    for i,j in enumerate(t1,1):
        if ch==i:
            s = scrape('https://imdb.com'+j.findChildren()[0].get('href'))
            try:
                print("-----\n{} has a rating of {}!\n".format(j.text,s.find('span',attrs={'itemprop':'ratingValue'}).text))
            except AttributeError:
                print("Rating for this title cannot be fetched right now...")

search()
