from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_ask import Ask
from flask_login import LoginManager
from flask_mail import Mail
from flask_restful import Api

app = Flask(__name__)
app.config['SECRET_KEY']='fhdusfhysrgygdsyfgsdyfgsdyfg'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

ask = Ask(app, "/alexa")

api = Api(app)

db=SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view='users.login'
login_manager.login_message_category='info'

mail = Mail()

from myflask import routes