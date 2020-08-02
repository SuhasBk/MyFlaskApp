import os
import base64
import json
import time
from threading import Thread
from datetime import date
from flask_restful import Resource
from myflask import api
from subprocess import run, PIPE
from flask import request

GLOBAL_ERROR_MESSAGE = ''

#Representational State Transfer:
class ApiDoc(Resource):
    def get(self):
        data = {
            'Corona WHO situation report': {'GET':'/api/coronastats'},
            'English dictionary': {'GET' : '/api/dictionary?word=<"word">', 'POST':['/api/dictionary','word']},
            'Weather' : {'GET': '/api/weather?country=<"country_name">&city=<"city_name">'},
            'IMDb' : {'GET': '/api/imdb?title=<"title">'},
            'Deccan Herald E-Paper' : {'GET' : ['/api/deccan', '/api/deccan?edition={0-8}']}
        }
        return {'response' : data}

class CoronaApi(Resource):
    def get(self):
        run(['python3', 'corona_status_report.py'], stdout=PIPE)
        pdf = open(f"myflask/static/report.pdf", "rb")
        contents = pdf.read()
        out = base64.b64encode(contents).decode('utf-8')
        pdf.close()
        os.remove(f"myflask/static/report.pdf")
        return {'response': out}, 201

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

            return { 'response': { '/api/deccan?edition=': {
                0: 'Bangalore',
                1: 'Davanagere',
                2: 'Gadag, Haveri, Ballari',
                3: 'Hubballi-Dharwad',
                4: 'Kalaburgi',
                5: 'Kolar, Chikkaballapur, Tumkuru',
                6: 'Mangaluru',
                7: 'Mysuru',
                8: 'Uttara Kannada, Belagavi City'
            }}}, 200
        else:

            thread = Thread(target=spinoff)
            thread.start()

            return {'response': f'epaper{edition}.pdf'}, 200

class Dict(Resource):
    def get(self):
        word = request.args.get('word')
        op = run(['python3', 'dict.py', word],stdout=PIPE)
        out = op.stdout.decode('utf-8')
        return {'response': out}, 201

    def post(self):
        data = request.get_json()
        if data != None and 'word' in data.keys():
            word = data.get("word")
            op = run(['python3', 'dict.py', word], stdout=PIPE)
            out = op.stdout.decode('utf-8')
            return {'response': out}, 201
        else:
            return {'response': "JSON Error"}, 400

class Weather(Resource):
    def get(self):
        country = request.args['country']
        city = request.args['city']
        op = run(['python3', 'weather.py',country,city], stdout=PIPE)
        out = op.stdout.decode('utf-8')
        return {'response': out}, 201

class IMDB(Resource):
    def get(self):
        title = request.args.get('title')
        p = run(['python3',"imdb.py",title],stdout=PIPE,input=b'1\n')
        out = p.stdout.decode('utf-8')
        out = out.split('-----\n')[1]
        return {'response':out},201

api.add_resource(ApiDoc, '/api')
api.add_resource(CoronaApi, '/api/coronastats')
api.add_resource(DeccanApi, '/api/deccan')
api.add_resource(Dict, '/api/dictionary')
api.add_resource(FileExists, '/api/find')
api.add_resource(Weather, '/api/weather')
api.add_resource(IMDB,'/api/imdb')
