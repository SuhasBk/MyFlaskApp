import datetime
import os
import random
import re
import sys
import time
from subprocess import PIPE, run
from threading import Thread
import requests
from bs4 import BeautifulSoup
from flask import (Flask, abort, flash, jsonify, redirect, render_template,request, url_for)
from flask_ask import question, statement
import myflask.api
from myflask.forms import (LoginForm, NewHandle, RegistrationForm, Search,UpdateForm)
from myflask.models import Account, Users
from . import app, bcrypt, db

@app.route("/",methods=['GET','POST'])
@app.route("/home",methods=['GET','POST'])
def home():
    return render_template('index.html')

@app.route("/youtube",methods=['GET','POST'])
def youtube():
    f = Search()
    if f.validate_on_submit():
        search = f.search.data
        r = requests.get("http://youtube.com/results?search_query=" + '+'.join(search.split(' ')))

        s = BeautifulSoup(r.text, 'html.parser')
        l = s.select('div .yt-lockup-content')
        urls = []

        for i in l:
            urls.append('http://youtube.com/embed'+i.find('a').get('href').replace('watch?v=',''))

        vids=urls[:20]

        return render_template('vids.html',posts=vids,title='YouTube')
    return render_template('home.html',title='YouTube',form=f)

# display my resume:
@app.route("/resume",methods=['GET','POST'])
def resume():
    if request.method=='POST':
        with open('myflask'+url_for('static',filename='my-resume.pdf'),'rb') as f:
            data = f.read()
        return data
    return render_template('resume.html',title = 'My Resume')

# random xkcd comic:
@app.route("/xkcd",methods=['GET','POST'])
def xkcd():
    try:
        r = requests.get("https://c.xkcd.com/random/comic/")
        data=BeautifulSoup(r.text,'html.parser').select('img')[2].get('src')
        img = 'http:'+data
        print(img)
        return render_template('vids.html',img=img,title='XKCD WebComics')
    except:
        return abort(500)

# lyrics scraper:
@app.route("/lyrics",methods=['GET','POST'])
def lyrics():
    form = Search()
    if form.validate_on_submit():
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
    return render_template('home.html',form=form,title='Lyrics')

# virtual piano renderer:
@app.route("/piano",methods=['GET','POST'])
def piano():
    return render_template('piano.html')

# register new user:
@app.route("/register",methods=['GET','POST'])
def register():
    rf = RegistrationForm()
    if rf.validate_on_submit():
        user = Users()
        user.user = rf.email.data
        user.passwd = bcrypt.generate_password_hash(rf.password.data)
        user.handles = rf.handles.data
        db.session.add(user)
        db.session.commit()
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

            flash('Incorrect username/password','danger')
        else:
            return abort(401)

    return render_template('login.html',purpose='Personalized Twitter!',form=lf)

# update email and password of twitter users:
@app.route("/user_update/<user>",methods=['GET','POST'])
def user_update(user):
    uf = UpdateForm()

    if uf.validate_on_submit():
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

    return render_template('twitter.html',handles=handles,user=u)

# add new twitter handles:
@app.route('/add_handle/<user>',methods=['GET','POST'])
def add_handle(user):
    new = NewHandle()

    if new.validate_on_submit():
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
    if subr.validate_on_submit():
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
    return render_template("home.html",form=subr,title = 'Reddit')

# get latest corona report from WHO:
@app.route("/corona",methods=['GET'])
def corona():
    run(['python3', 'corona_status_report.py'], stdout=PIPE)
    return render_template("corona.html", name="report.pdf")

# Deccan Herald E-Paper mail service:
def send_paper(recepient_email,sender_email,sender_password):
    if 'epaper.pdf' in os.listdir():
        raw_time = os.stat('epaper.pdf').st_mtime
        mod_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(raw_time))
        if str(datetime.datetime.today().date()) == mod_time.split()[0]:
            op = run(['python3', 'deccan.py', recepient_email,sender_email,sender_password,'file_exists'], stdout=PIPE)
    else:
        op = run(['python3', 'deccan.py', recepient_email,sender_email,sender_password], stdout=PIPE)

@app.route("/deccan",methods=["GET","POST"])
def deccan():
    if request.method == 'POST':
        try:            
            account = Account.query.limit(1).all()[0]
            
            recipient_email = request.form.get('mail')
            sender_email = account.email
            sender_password = account.passwd

            Thread(target=send_paper,args=(recipient_email,sender_email,sender_password,)).start()
            
            return f"<title>Success</title><h1>Today's epaper will be sent to <em>{recipient_email}</em> within the next 5-10 minutes.</h1><br><h2>Thank you for your patience</h2>"
        except:
            return f"<title>Error</title><h1 style='color:red;'>Admin account not setup.</h1><br><br><h3>Register your own at <a href='{url_for('admin')}'>Account setup</a></h3>"
    else:
        return render_template("deccan_mail.html")

@app.route("/admin",methods=["GET","POST"])
def admin():
    if request.method == 'POST':
        email = request.form.get('mail')
        password = request.form.get('pwd')

        account = Account()
        account.email = email
        account.passwd = password

        try:
            db.session.add(account)
        except:
            return "<h1>An account is already registered for sending mails... Can't override...</h1>"
        else:
            db.session.commit()
            return f"<h1 style='color:green'>All set! This email account will be used for sending mails...</h1><br><br><h2>Go back to <a href='{url_for('deccan')}'>Deccan Herald epaper</a></h2>"
    else:
        return render_template("admin.html")

# hard reset database in case of schema problems:
@app.route("/reset/true")
def refresh():
    db.drop_all()
    db.create_all()
    return redirect(url_for('home'))
