from flask_wtf import FlaskForm
from myflask import db
from myflask.models import Twitter
from wtforms import StringField,SubmitField,RadioField,PasswordField,BooleanField
from wtforms.validators import DataRequired,Email

class Search(FlaskForm):
    search = StringField('Enter the search term:')
    submit = SubmitField('Search')

class NewHandle(FlaskForm):
    handle_name = StringField("Enter the '@' handle of a Twitter account...(Ex : if handle is '@handle_name', then type 'handle_name') : ",validators=[DataRequired()])
    submit = SubmitField('Add it to the list')

class LoginForm(FlaskForm):
    email = StringField('E-mail',validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    remember=BooleanField('Remember Me')
    submit=SubmitField('Login')
