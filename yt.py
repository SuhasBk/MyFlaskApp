#!/usr/bin/python3
import os
import re
import sys
import requests
from bs4 import BeautifulSoup

def fetch_urls(search_term):
    try:
        r = requests.get("https://youtube.com/results?search_query=" + '+'.join(search_term.split()), headers={'user-agent':'my-web-app'})
    except requests.HTTPError as err:
        print(err)
        exit()

    s = BeautifulSoup(r.text, 'html.parser')

    data = str(s.findAll('script')[26])

    video_ids = re.findall(r'\"/watch\?v=(.{11})\"', data)
    urls = list(map(lambda id : "http://youtube.com/embed/"+id, video_ids))

    return urls
