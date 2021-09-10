#!/usr/bin/python3
import re
import requests

def fetch_urls(search_term):
    try:
        r = requests.get("http://youtube.com/results?search_query=" + '+'.join(search_term.split()))
    except requests.HTTPError as err:
        print(err)
        exit()

    urls = re.findall('{"videoId":"(\w+)"', r.text)
    urls = list(map(lambda x: 'https://youtube.com/embed/' + x, (sorted(set(urls), key=urls.index))))
    return urls