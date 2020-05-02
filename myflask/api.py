import os
import base64
import json
from datetime import date
from flask_restful import Resource
from myflask import api
from subprocess import run, PIPE
from flask import request

#Representational State Transfer:
class DeccanApi(Resource):
    def get(self):
        r = run(["python3", "deccan.py"], env={'HIDDEN_ID': "BATMAN", 'PATH': os.environ['PATH']})

        if r.returncode == 42:
            return {'response': "Dependencies not resolved !!!"}, 500

        name = '_'.join(str(date.today()).split('-')[::-1])+'_epaper.pdf'
        pdf = open(name, "rb")
        contents = pdf.read()
        out = base64.b64encode(contents).decode('utf-8')
        pdf.close()
        return {'response': out}, 201


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


api.add_resource(CoronaApi, '/coronastats')
api.add_resource(Dict, '/dictionary')
api.add_resource(Weather, '/weather')
api.add_resource(DeccanApi, '/deccan')
api.add_resource(IMDB,'/imdb')
