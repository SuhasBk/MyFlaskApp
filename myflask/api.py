import os
import base64
import json
import time
from datetime import date
from flask_restful import Resource
from myflask import api
from subprocess import run, PIPE
from flask import request

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

class DeccanApi(Resource):
    def get(self):
        edition = request.args.get('edition')
        
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
            op = run(['python3', 'deccan.py', edition], stdout=PIPE, stderr=PIPE)

            pdf_file_name = op.stdout.decode('utf-8').strip()
            errors = op.stderr.decode('utf-8').strip()
            
            if errors:
                return {'response': False, 'message': 'Something went wrong, try again later!', 'data': errors}, 500
            else:
                contents = open(pdf_file_name,"rb").read()
                out = base64.b64encode(contents).decode('utf-8')
                return {'response': True, 'file_name': pdf_file_name, 'data': out}, 200

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
api.add_resource(Weather, '/api/weather')
api.add_resource(IMDB,'/api/imdb')
