#!/usr/bin/python3

from requests import Session
from bs4 import BeautifulSoup
from datetime import date
import re

s = Session()
r = s.get("http://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports")
html = BeautifulSoup(r.text,'html.parser')

pdf_url = html.find('a', text=re.compile(r'Update - \d+')).get('href')
full_url = "https://" + r.url.split('/')[2] + pdf_url

p = s.get(full_url)
open(f"myflask/static/report.pdf","wb+").write(p.content)
s.close()
