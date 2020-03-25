from flask import render_template,url_for,flash,redirect,request,abort,jsonify,send_from_directory
from flask_ask import question,statement
from myflask.forms import Search,NewHandle,LoginForm,RegistrationForm,UpdateForm
from myflask.models import Users
from flask import Flask
from myflask import app,db,ask,api,bcrypt
import os,random,re,time,sys,requests
from flask_restful import Resource
from bs4 import BeautifulSoup
from subprocess import run,PIPE
import base64,json
from datetime import date

#Representational State Transfer:
class DeccanApi(Resource):
    def get(self):
        r = run(["python3", "deccan.py"], env={'HIDDEN_ID': "BATMAN", 'PATH': os.environ['PATH']})

        if r.returncode == 42:
            return {'response':"Dependencies not resolved !!!"}

        name = '_'.join(str(date.today()).split('-')[::-1])+'_epaper.pdf'
        pdf = open(name, "rb")
        contents = pdf.read()
        out = base64.b64encode(contents).decode('utf-8')
        pdf.close()
        return {'response': out}, 201
        
class CoronaApi(Resource):
    def get(self):
        run(['python3','corona_status_report.py'],stdout=PIPE)
        pdf = open(f"myflask/static/report.pdf","rb")
        contents = pdf.read()
        out = base64.b64encode(contents).decode('utf-8')
        pdf.close()
        os.remove(f"myflask/static/report.pdf")
        return {'response':out},201

class Dict(Resource):
    def get(self):
        word = request.args['word'].encode('utf-8')
        op = run(['python3','dict.py',word],stdout=PIPE)
        out = op.stdout.decode('utf-8')
        return {'response':out},201
    def post(self):
        data = request.get_json()
        if data!=None and 'word' in data.keys():
            word = data.get("word")
            op = run(['python3','dict.py',word],stdout=PIPE)
            out = op.stdout.decode('utf-8')
            return {'response':out},201
        else:
            return {'response':"JSON Error"},400

class Weather(Resource):
    def get(self):
        country = request.args['country']
        city = request.args['city']
        parameter = (country+'\n'+city).encode('utf-8')
        op = run(['python3','weather.py'],input=parameter,stdout=PIPE)
        out = op.stdout.decode('utf-8').split('\n> ')[2]
        return {'response':out},201

api.add_resource(CoronaApi,'/coronastats')
api.add_resource(Dict,'/dictionary')
api.add_resource(Weather,'/weather')
api.add_resource(DeccanApi,'/deccan')

#ALEXA!!!!
@app.route('/alexa')
def alexa():
    return render_template('alexa.html')

@ask.launch
def start_skill():
    welcome = "Hello human! Hyperbyte is online. Say features, to see what Suhas has programmed me to do!"
    return question(welcome)

@ask.intent("FeaturesIntent")
def features_intent():
    features = "Say quote, for quotes! Say repeat, followed by phrase to be repeated, for mimicry! Say knock knock, for knock knock jokes! Say imdb and the title, for ratings! These are all the fantastic stuffs Suhas programmed me to do."
    return question(features)

@ask.intent("QuoteIntent")
def yes_intent():
    r=requests.get("https://www.eduro.com/")
    p=BeautifulSoup(r.text,'html.parser').findAll('p',attrs={'class':''})
    quotes = []
    for i in range(0,len(p)-1,2):
        quotes.append(p[i].text)
    quote = random.choice(quotes)
    return question(quote)

@ask.intent("NoIntent")
def no_intent():
    bye_text = "Bye buddy... Thanks for checking me out."
    return statement(bye_text)

@ask.intent('DictIntent', mapping={'word': 'Query'})
def dictionary(word):
    op = run(['python3','dict.py',word],stdout=PIPE)
    out = op.stdout.decode('utf-8')
    return question(out)

@ask.intent("RepIntent", mapping={'word': 'Phrase'})
def repeat(word):
    print(word)
    if word == None:
        return question('Whats that?')
    else:
        return question(word)

@ask.intent("KnockIntent")
def knock():
    r=requests.get("https://thoughtcatalog.com/melanie-berliet/2015/09/40-ridiculous-knock-knock-jokes-thatll-get-you-a-laugh-on-demand/")
    s = BeautifulSoup(r.text,'html.parser')
    k = s.find('div',attrs={'class':'box-content'}).text
    jokes = re.split(r'[\d+]',k)
    joke = random.choice(jokes)
    joke = joke.replace('.','')
    print(joke.encode('utf-8').rstrip())
    return question(joke)

@ask.intent("IMDbIntent", mapping={'title':'Title'})
def imdb(title):
    p = run(['python3',"imdb.py",title],stdout=PIPE,input=b'1\n')
    out = p.stdout.decode('utf-8')
    out = out.split('-----\n')[1]
    return question(out)
#ALEXA!!!

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
        r=requests.get("https://c.xkcd.com/random/comic/")
        data=BeautifulSoup(r.text,'html.parser').select('img')[2].get('src')
        img='http:'+data
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

# random file download from server:
@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = app.config['UPLOAD_FOLDER']
    return send_from_directory(directory=uploads, filename=filename, as_attachment=True)


# for testing new features:
@app.route("/corona",methods=['GET'])
def corona():
    run(['python3', 'corona_status_report.py'], stdout=PIPE)
    return render_template("corona.html", name="report.pdf")

# reset database in case of any problems:
@app.route("/r")
def refresh():
    db.drop_all()
    db.create_all()
    return redirect(url_for('home'))
