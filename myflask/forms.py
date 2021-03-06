from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,RadioField,PasswordField,BooleanField
from wtforms.validators import DataRequired,Email

class Search(FlaskForm):
    search = StringField('Enter the search term:')
    submit = SubmitField('Search')

class NewHandle(FlaskForm):
    handle_name = StringField("Enter the '@' handle of a Twitter account...\n(Ex : if handle is '@handle_name', then type 'handle_name') : ",validators=[DataRequired()])
    submit = SubmitField('Add it to the list')

class RegistrationForm(FlaskForm):
    email = StringField('E-mail',validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    handles=StringField('Handles To follow')
    submit=SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('E-mail',validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('Sign In')

class UpdateForm(FlaskForm):
    email = StringField('Update E-mail',validators=[Email()])
    password = PasswordField('Update Password')
    submit = SubmitField('Update')
