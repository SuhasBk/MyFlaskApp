import os
import base64
import json
from datetime import date
from flask_restful import Resource
from myflask import api
from subprocess import run, PIPE
from flask import request

#Representational State Transfer:
class ApiDoc(Resource):
    def get(self):
        data = "1. Corona WHO situation report -> (GET) /api/coronastats\n2. English dictionary -> (GET,POST) /api/dictionary?word=<'word'>\n3. Weather updates -> (GET) /api/weather?country=<'country_name'>&city=<'city_name'>\n4. IMDb ratings -> (GET) /api/imdb?title=<'title'>."
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
api.add_resource(Dict, '/api/dictionary')
api.add_resource(Weather, '/api/weather')
api.add_resource(IMDB,'/api/imdb')
