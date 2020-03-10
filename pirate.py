#!/usr/bin/python3
import requests,sys,time
from bs4 import BeautifulSoup

goods = ' '.join(sys.argv[1:])

headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'}

try:
    print(f"Searching for {goods}...\nTrying first server...")
    r = requests.get(f"https://thepiratebay.org/search/{goods}",headers=headers,timeout=5)
except requests.exceptions.ReadTimeout:
    print("\nFailed!!! Trying second server...")
    r = requests.get(f"https://pirateproxy.ink/search/{goods}",headers=headers)
    if not r.ok:
        exit("Servers are down! :(")
    
base_torrent_url = r.url[:r.url.find('search')-1]

torrent_data = { 'title' : [], 'torrent_url' : [] }


d = BeautifulSoup(r.text,'html.parser').findAll('a',{'class':'detLink'})

torrent_data['title'] = list(map(lambda x : x.text, d))
torrent_data['torrent_url'] = list(map(lambda x : base_torrent_url+x.get('href'), d))

for link in torrent_data['torrent_url'][:10]:
    try:
        print("\n<<< "+str(torrent_data['torrent_url'].index(link) + 1)+" >>> : TITLE : ",
                torrent_data['title'][torrent_data['torrent_url'].index(link)])
        tp = requests.get(link,headers=headers)
        s = BeautifulSoup(tp.text,'html.parser')
        print("SIZE : ",s.find('dl', {'class': 'col1'}).findAll('dd')[2].text)
        print("UPLOADED ON : ",s.find('dl',{'class':'col2'}).findAll('dd')[0].text)
        print("UPLOADED BY : ",s.find('dl',{'class':'col2'}).findAll('dd')[1].text)
        print("MAGENT LINK : ",s.find('div',{'class':'download'}).find('a').get('href'))
        print("TORRENT PAGE URL : ",tp.url)
        time.sleep(0.5)
    except:
        pass



