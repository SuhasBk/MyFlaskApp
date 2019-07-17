#!/usr/bin/python3
import requests
from bs4 import *
import sys

if len(sys.argv) > 1:
    word = sys.argv[1]
else:
    word = input("Enter the word\n")

try:
    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'}
    r = requests.get("https://dictionary.cambridge.org/dictionary/english/{}".format(word),headers=headers)
    s = BeautifulSoup(r.text,'html.parser')
    sections = s.findAll('div',attrs={'class':'sense-body'})
    meaning = ''
    for i in sections:
        meaning += i.text
    print("Word : '{}'\n\nMeaning : {}".format(word,meaning))
except AttributeError:
    print('No such word in my dictionary...')
