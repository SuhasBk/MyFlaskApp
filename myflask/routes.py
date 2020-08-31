import datetime
import os
import random
import re
import sys
import time
import json
from subprocess import PIPE, run
from threading import Thread
import requests
from bs4 import BeautifulSoup
from flask import (Flask, abort, flash, jsonify, redirect, render_template,request, url_for, send_file)
import myflask.api
from myflask.forms import (LoginForm, NewHandle, RegistrationForm, Search,UpdateForm)
from myflask.models import Users
from . import app, bcrypt, db

@app.route("/",methods=['GET','POST'])
@app.route("/home",methods=['GET','POST'])
def home():
    return render_template('index.html')

@app.route("/youtube",methods=['GET','POST'])
def youtube():
    form = Search()

    if form.validate_on_submit() or request.method == 'POST':
        search_term = form.search.data

        data = {'search_term': search_term}
        yt_api = requests.post(f"{request.url_root}api/yt", json=data)
        yt_api_response = yt_api.json()

        if yt_api_response['success']:
            vids = json.loads(yt_api_response['urls'])
            return render_template('vids.html',posts=vids,title='YouTube')
        else:
            return abort(500)

    return render_template('input.html',title='YouTube',form=form)

# display my resume:
@app.route("/resume",methods=['GET','POST'])
def resume():
    return send_file("static/my-resume.pdf")

# random xkcd comic:
@app.route("/xkcd",methods=['GET','POST'])
def xkcd():
    xkcd_api = requests.get(f"{request.url_root}api/xkcd")
    xkcd_api_response = xkcd_api.json()
    
    if xkcd_api_response['success']:
        img = xkcd_api_response['img']
        return render_template('vids.html', img=img, title='XKCD WebComics')
    else:
        return abort(500)

# lyrics scraper:
@app.route("/lyrics",methods=['GET','POST'])
def lyrics():
    form = Search()
    if form.validate_on_submit() or request.method == 'POST':
        flash('Click on the links below!','info')
        r=requests.get("https://search.azlyrics.com/search.php?q="+'+'.join(form.search.data.split()))
        s=BeautifulSoup(r.text,'html.parser')
        td=s.findAll('td',attrs={'class':'text-left visitedlyr'})
        res=[]
        for i in td[:5]:
            s=re.findall(r'<b>.*</b>',str(i))[0]
            for r in (('<b>',''),('</b>',''),('</a>','')):
                s=s.replace(*r)
            res.append([i.find('a').get('href'),s])
        return render_template('lyrics.html',res=res,title=form.search.data.upper()+' LYRICS')
    return render_template('input.html',form=form,title='Lyrics')

# register new user:
@app.route("/register",methods=['GET','POST'])
def register():
    rf = RegistrationForm()
    if rf.validate_on_submit() or request.method == 'POST':
        user = Users()
        user.user = rf.email.data
        user.passwd = bcrypt.generate_password_hash(rf.password.data)
        user.handles = rf.handles.data
        try:
            db.session.add(user)
            db.session.commit()
        except:
            flash("Username/email already exists... Please try again...", "danger")
        else:
            return redirect(url_for('login'))
    return render_template('register.html',form=rf,purpose='Personalized Twitter!')

# user login:
@app.route("/login",methods=['GET','POST'])
def login():
    lf = LoginForm()

    if request.method == 'POST':
        if lf.validate_on_submit():
            who = lf.email.data
            user = Users.query.filter_by(user=who).first()

            if user:
                check = bcrypt.check_password_hash(user.passwd,lf.password.data)
                
                if check:
                    return redirect(url_for('twitter',user=user.user))

        flash('Incorrect username/password.. Try again or sign up now!','danger')
    return render_template('login.html',purpose='Personalized Twitter!',form=lf)

# update email and password of twitter users:
@app.route("/user_update/<user>",methods=['GET','POST'])
def user_update(user):
    uf = UpdateForm()

    if uf.validate_on_submit() or request.method == 'POST':
        u = Users.query.filter_by(user=user).first()
        if uf.email.data or uf.password.data:
            if uf.email.data != '':
                u.user = uf.email.data
            if uf.password.data != '':
                u.passwd = bcrypt.generate_password_hash(uf.password.data)
            db.session.commit()
            flash('Account updated successfully','info')
        else:
            flash('Account unchanged!','info')
        return redirect(url_for('twitter'))
    return render_template('update.html',form=uf)

# view twitter homepage with custom handles:
@app.route("/twitter",defaults={'user':''},methods=['GET','POST'])
@app.route("/twitter/<user>",methods=['GET','POST'])
def twitter(user):
    if user=='':
        return redirect(url_for('login'))

    u = Users.query.filter_by(user=user).first()
    handles = u.handles.split(',')

    return render_template('twitter.html',handles=handles,user=u,title="Personalized Twitter")

# add new twitter handles:
@app.route('/add_handle/<user>',methods=['GET','POST'])
def add_handle(user):
    new = NewHandle()

    if new.validate_on_submit() or request.method == 'POST':
        h = new.handle_name.data
        try:
            u = Users.query.filter_by(user=user).first()
            if h in u.handles:
                raise ValueError
            u.handles += ','+h
            db.session.commit()
            return redirect(url_for('twitter',user=user))
        except ValueError:
            flash('{} already exists!!!'.format(h),'danger')

    return render_template('add_handle.html',form=new)

# remove twitter handles:
@app.route('/remove_handle/<user>/<handle>',methods=['GET'])
def remove_handle(user,handle):
    u = Users.query.filter_by(user=user).first()
    handles = u.handles.split(',')

    if handle == '*':
        u.handles=''

    elif handle not in handles:
        flash("{} does not exist!".format(handle),"danger")

    else:
        handles.remove(handle)
        u.handles = ','.join(handles)
    db.session.commit()
    return redirect(url_for('twitter',user=u))

# subreddit scraper:
@app.route("/reddit",methods=['GET','POST'])
def reddit():
    subr = Search()
    if subr.validate_on_submit() or request.method == 'POST':
        username='Suhasbk98'
        passwd=os.environ.get('REDPWD')
        sub = subr.search.data
        user={'user':username,'passwd':passwd,'api_type':'json'}

        s=requests.Session()
        s.headers.update({'user-agent':'boom'})
        s.post('https://reddit.com/api/login',data=user)
        time.sleep(1)

        html=s.get('https://reddit.com/r/{}/.json?limit=20'.format(sub)).json()
        content=html['data']['children']

        return render_template("reddit.html",data=content,sub=sub)
    return render_template("input.html",form=subr,title='Reddit')

# hard reset database in case of schema problems:
@app.route("/reset/true")
def refresh():
    db.drop_all()
    db.create_all()
    return redirect(url_for('home'))
