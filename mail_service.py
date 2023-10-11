#!/usr/bin/python3
import requests

def portfolioMonitor(url, ip):
    requests.post(f"{url}api/portfoliomonitor", json={'IP': ip})