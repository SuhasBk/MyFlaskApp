import os
import base64
import json
import time
import requests
from yt import fetch_urls
from bs4 import BeautifulSoup
from threading import Thread
from datetime import date
from flask_restful import Resource
from myflask import api
from subprocess import run, PIPE
from flask import request

GLOBAL_ERROR_MESSAGE = ''

# Representational State Transfer:
class ApiDoc(Resource):
    def get(self):
        data = {
            'English dictionary': {
                'GET request' : {
                    'endpoint': '/api/dictionary?word=<word>',
                    'description': 'returns meaning of the word as a string'
                },
                'POST request': {
                    'endpoint': '/api/dictionary',
                    'json_body': '{word : <word>}',
                    'description': 'returns meaning of the word as a string'
                }
            },
            'Weather details' : {
                'GET request': {
                    'endpoint': '/api/weather?country=<country_name>&city=<city_name>',
                    'description': 'returns weather details as a string'
                }
            },
            'IMDb ratings' : {
                'GET request': {
                    'endpoint': '/api/imdb?title=<title>',
                    'description': 'returns title\'s rating as a string'
                }
            },
            'Deccan Herald E-Paper' : {
                'GET request 1' : {
                    'endpoint': '/api/deccan',
                    'description': 'returns DH edition details',
                },
                'GET request 2': {
                    'endpoint': '/api/deccan?edition={0-8}',
                    'description': 'starts a background thread to download PDF, returns file name as a string'
                }
            },
            'Check if a file exists in server' : {
                'GET request': {
                    'endpoint': '/api/find?file=<file_name>',
                    'description': 'returns true if file_name exists else false'
                }
            },
            'World Clock': {
                'GET request': {
                    'endpoint': '/api/clock?city=<city>',
                    'description': 'returns current time and date as string in any city in the world.'
                }
            },
            'Random XKCD comic': {
                'GET request': {
                    'endpoint': '/api/xkcd',
                    'description': 'returns a random XKCD comic image url.'
                }
            },
            'YouTube URLS': {
                'POST request': {
                    'endpoint': '/api/yt',
                    'json_body': '{ search_term: <search_term> }',
                    'description': 'returns 10 youtube embed urls based on search results.'
                }
            }
        }
        return {'response' : data}

class DeccanApi(Resource):

    def get(self):
        edition = request.args.get('edition')

        def spinoff():
            global GLOBAL_ERROR_MESSAGE
            op = run(['python3', 'deccan.py', edition], stdout=PIPE, stderr=PIPE)
            errors = op.stderr.decode('utf-8')

            if errors:
                GLOBAL_ERROR_MESSAGE = errors

        if not edition:
            return { 
                'response': { 
                    '/api/deccan?edition=': {
                        0: 'Bangalore',
                        1: 'Davanagere',
                        2: 'Gadag, Haveri, Ballari',
                        3: 'Hubballi-Dharwad',
                        4: 'Kalaburgi',
                        5: 'Kolar, Chikkaballapur, Tumkuru',
                        6: 'Mangaluru',
                        7: 'Mysuru',
                        8: 'Uttara Kannada, Belagavi City'
                    }
                }
            }, 200
        else:
            Thread(target=spinoff).start()
            return {
                'response': f'epaper{edition}.pdf'
            }, 200

class Dict(Resource):
    def get(self):
        word = request.args.get('word')
        op = run(['python3', 'dict.py', word],stdout=PIPE)
        out = op.stdout.decode('utf-8').strip()
        return { 'response': out }, 200

    def post(self):
        data = request.get_json()
        if data != None and 'word' in data.keys():
            word = data.get("word")
            op = run(['python3', 'dict.py', word], stdout=PIPE)
            out = op.stdout.decode('utf-8')
            return {'response': out}, 201
        else:
            return {'response': "JSON Error"}, 400

class FileExists(Resource):
    def get(self):
        global GLOBAL_ERROR_MESSAGE
        file_name = request.args.get('file')

        if file_name in os.listdir():
            return {'response': True}, 200
        elif GLOBAL_ERROR_MESSAGE:
            return {'response': False, 'errors': GLOBAL_ERROR_MESSAGE}
        else:
            return {'response': False}, 200

class IMDB(Resource):
    def get(self):
        title = request.args.get('title')
        p = run(['python3', "imdb.py", title], stdout=PIPE, input=b'1\n')
        out = p.stdout.decode('utf-8')
        out = out.split('-----\n')[1].strip()
        return {'response': out}, 200

class Weather(Resource):
    def get(self):
        country = request.args.get('country')
        city = request.args.get('city')
        op = run(['python3', 'weather.py',country,city], stdout=PIPE)
        out = op.stdout.decode('utf-8').strip()
        return {'response': out}, 200

class WorldClock(Resource):
    def get(self):
        city = request.args.get('city')
        op = run(['python3', 'world_clock.py', city], stdout=PIPE)
        out = op.stdout.decode('utf-8').replace('\t',', ').strip()
        return {'response': out}, 200

class XKCDApi(Resource):
    def get(self):
        try:
            xkcd_http = requests.get("https://c.xkcd.com/random/comic/")
            url = BeautifulSoup(xkcd_http.text, 'html.parser').select('img')[2].get('src')
            img = 'http:'+url
            return {'success': True, 'img': img}
        except:
            return {'success': False}

class YouTubeApi(Resource):
    def post(self):
        data = request.get_json()
        search_term = data['search_term']
        urls = fetch_urls(search_term)[:10]

        if urls:
            return {'success':True, 'urls': json.dumps(urls)}
        else:
            return {'success':False}


api.add_resource(ApiDoc, '/api')
api.add_resource(DeccanApi, '/api/deccan')
api.add_resource(Dict, '/api/dictionary')
api.add_resource(IMDB, '/api/imdb')
api.add_resource(FileExists, '/api/find')
api.add_resource(Weather, '/api/weather')
api.add_resource(WorldClock, '/api/clock')
api.add_resource(XKCDApi, '/api/xkcd')
api.add_resource(YouTubeApi, '/api/yt')