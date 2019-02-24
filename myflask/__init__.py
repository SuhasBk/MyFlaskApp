from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_ask import Ask
from flask_login import LoginManager
from flask_mail import Mail
from flask_restful import Resource, Api

app = Flask(__name__)
app.config['SECRET_KEY']='fhdusfhysrgygdsyfgsdyfgsdyfg'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

ask = Ask(app, "/alexa")

api = Api(app)

class GuruKul(Resource):
    def post(self):
        from subprocess import Popen,PIPE
        data = request.get_json()
        if 'usn' in data and 'password' in data:
            p=Popen(["guru.py",data['usn'],data['password']],stdout=PIPE,stderr=PIPE)
            out,err = p.communicate()
            return {'request':data,'response':out},201
        else:
            return {'request':data,'response':"JSON KeyError"},400
api.add_resource(GuruKul,'/gurukul')

class SongLyr(Resource):
    search_results = []
    links = []

    def get(self):
        return {'response':'Welcome to Lyrics Scraper!'}

    def post(self):
        import requests,re
        from bs4 import BeautifulSoup

        data = request.get_json()

        if 'song' in data:
            p=data['song'].split()
            r=requests.get("https://search.azlyrics.com/search.php?q="+'+'.join(p))

            s=BeautifulSoup(r.text,'html.parser')
            td=s.findAll('td',attrs={'class':'text-left visitedlyr'})

            for i,j in enumerate(td[:5]):
                s=re.findall(r'<b>.*</b>',str(j))[0]
                for r in (('<b>',''),('</b>',''),('</a>','')):
                    s=s.replace(*r)
                self.search_results.append([i,s])
                self.links.append(j.find('a').get('href'))

            return {'response':self.search_results},201

        elif 'option' in data:
            self.search_results=[]
            for i,j in zip(list(range(0,len(self.links))),self.links):
                if data['option']==i:
                    q=requests.get(j)
                    s=BeautifulSoup(q.text,'html.parser')
                    try:
                        l=s.find('div',attrs={'class':'col-xs-12 col-lg-8 text-center'}).find('div',attrs={'class':''})
                    except:
                        l=None
                    if l!=None:
                        self.links = []
                        lyrics = l.text
                        return {'response':lyrics},201
                    else:
                        return{'response':'The requested lyrics can not be found! Please select another'}
        else:
            return {'request':data,'response':"JSON KeyError"},400
        pass

api.add_resource(SongLyr,"/songlyr")

db=SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view='users.login'
login_manager.login_message_category='info'

mail = Mail()

from myflask import routes
