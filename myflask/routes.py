from flask import render_template,url_for,flash,redirect,request,abort,jsonify,send_from_directory
from flask_ask import question,statement,session,delegate
from myflask.forms import Search,NewHandle,LoginForm
from myflask.models import Nice,Twitter
from flask import Flask
from myflask import app,db,ask,api
import os,random,re,time,sys,requests,markdown
from flask_restful import Resource
from bs4 import BeautifulSoup
from subprocess import run,PIPE

#Representational State Transfer:
class MyGurukul(Resource):
    def get(self):
        return {'response':"Woah!! How did you reach here? Please go back to what you were doing. No offence, but you don't belong here."}
    def post(self):
        data = request.get_json()
        if 'usn' in data.keys() and 'password' in data.keys():
            usn=data.get('usn')
            passwd=data.get('password')
            op = run('guru.py {} {}  a'.format(usn,passwd),input=b'exit',stdout=PIPE,shell=True)
            out = op.stdout.decode('utf-8')
            out = out.split('Please')[0]
            return {'request':data,'response':out},201
        else:
            return {'request':data,'response':"JSON KeyError"},400

class CricketLive(Resource):
    def get(self):
        from subprocess import run,PIPE
        op = run('cric.py',shell=True,stdout=PIPE)
        out = op.stdout.decode('utf-8')
        return {'response':out},200

api.add_resource(MyGurukul,'/gurukul')
api.add_resource(CricketLive,'/cricket')

#ALEXA!!!!
@app.route('/alexa')
def alexa():
    return render_template('alexa.html')

@ask.launch
def start_skill():
    welcome = "Hello boss! Hyperbyte is online. quote, for quotes! dict and the word, for dictionary! repeat, and the phrase to be repeated, for mimicry! knock knock, for knock knock jokes! imdb and the title, for movie ratings! These are all the fantastic stuffs Suhas programmed me to do."
    return question(welcome)

@ask.intent("QuoteIntent")
def yes_intent():
    r=requests.get("https://www.eduro.com/")
    p=BeautifulSoup(r.text,'html.parser').findAll('p',attrs={'class':''})
    quotes = []
    for i in range(0,len(p)-1,2):
        quotes.append(p[i].text.encode('utf-8'))
    quote = random.choice(quotes)
    return question(quote)

@ask.intent("NoIntent")
def no_intent():
    bye_text = "Bye buddy... Thanks for checking me out."
    return statement(bye_text)

@ask.intent('DictIntent', mapping={'word': 'Query'})
def dictionary(word):
    r=requests.get("https://www.dictionary.com/browse/{}".format(word))
    s=BeautifulSoup(r.text,'html.parser')
    try:
        meaning=s.find('ol',attrs={'class':'css-zw8qdz e1hk9ate4'}).text.encode('utf-8').split('Explore Dictionary')[0]
    except:
        return statement("No such word found! Sorry... try again")
    return question('The meaning of {} is {}?'.format(word,meaning))

@ask.intent("RepIntent", mapping={'word': 'Phrase'})
def repeat(word):
    print(word)
    if word == None:
        return question('What the fuck do you want me to repeat?')
    else:
        return question(word)

@ask.intent("KnockIntent")
def knock():
    r=requests.get("https://thoughtcatalog.com/melanie-berliet/2015/09/40-ridiculous-knock-knock-jokes-thatll-get-you-a-laugh-on-demand/")
    s = BeautifulSoup(r.text,'html.parser')
    k = s.find('div',attrs={'class':'box-content'}).text
    jokes = re.split('[\d+]',k)
    joke = random.choice(jokes)
    joke = joke.replace('.','')
    print(joke.encode('utf-8').rstrip())
    return question(joke)

@ask.intent("IMDbIntent", mapping={'title':'Title'})
def imdb(title):
    import subprocess
    from subprocess import PIPE
    p = subprocess.run(["imdb.py"],stdout=PIPE,stderr=PIPE,input='{}\n1\n'.format(title),encoding='ascii')
    out = p.stdout
    err = p.stderr
    out = out.split('-----\n')[1]
    if err == '':
        return question(out)
    else:
        return statement("No such movie or tv series found....")
#ALEXA!!!

@app.route("/",methods=['GET','POST'])
@app.route("/home",methods=['GET','POST'])
def home():
    return render_template('index.html')

@app.route("/youtube",methods=['GET','POST'])
def youtube():
    try:
        db.drop_all()
        db.create_all()
    except:
        pass
    f = Search()
    if f.validate_on_submit():
        search = f.search.data
        r = requests.get("http://youtube.com/results?search_query=" + '+'.join(search.split(' ')))

        s = BeautifulSoup(r.text, 'html.parser')
        l = s.select('div .yt-lockup-content')
        urls = []

        for i in l:
            urls.append('http://youtube.com/embed'+i.find('a').get("href").replace('watch?v=',''))

        vids=urls[:20]

        for i in vids:
            new = Nice(url=str(i))
            db.session.add(new)
            db.session.commit()
        links = Nice.query.all()
        return render_template('vids.html',posts=links,title='YouTube')
    return render_template('home.html',title='YouTube',form=f)

@app.route("/resume")
def resume():
    return render_template('resume.html',title = 'My Resume')

@app.route("/xkcd",methods=['GET','POST'])
def xkcd():
    try:
        db.drop_all()
        db.create_all()
    except:
        pass

    try:
        r=requests.get("http://c.xkcd.com/random/comic/")
        text=r.text
        data=BeautifulSoup(text,'html.parser').select('img')[3].get('src')
        img=Nice(url='http:'+data)
        db.session.add(img)
        db.session.commit()
        links = Nice.query.all()
        return render_template('vids.html',posts=links,title='XKCD WebComics')
    except:
        return abort(500)

@app.route("/lyrics",methods=['GET','POST'])
def lyrics():
    try:
        db.drop_all()
        db.create_all()
    except:
        pass
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

@app.route("/piano",methods=['GET','POST'])
def piano():
    return render_template('piano.html')

@app.route("/twitter",methods=['GET','POST'])
def twitter():
    handles = [['None',0]]
    new = NewHandle()

    if new.validate_on_submit():
        h = new.handle_name.data
        try:
            add = Twitter(handle_name=h)
            db.session.add(add)
            db.session.commit()
            flash('{} successfully added!'.format(h),'success')
            extras = [[str(i),i.id] for i in Twitter.query.all()]
            handles.extend(extras)
            print(handles)
            return render_template('twitter.html',handles=handles,new=new)
        except:
            flash('{} already exists!!!'.format(h),'danger')

    extras = [[str(i),i.id] for i in Twitter.query.all()]
    handles.extend(extras)
    return render_template('twitter.html',handles=handles,new=new)

@app.route('/remove_handle/<int:id>',methods=['GET','POST'])
def remove_handle(id):
    if id != 0:
        handle = Twitter.query.get(id)
        try:    #integrity constraints... last element cannot be deleted!
            db.session.delete(handle)
            db.session.commit()
            flash('{} removed!'.format(handle.handle_name),'danger')
        except:
            flash('{} removed!'.format(handle.handle_name),'danger')
            db.drop_all()
            db.create_all()
        return redirect(url_for('twitter'))
    else:
        abort(404)

@app.route("/reddit",methods=['GET','POST'])
def reddit():
    subr = Search()
    if subr.validate_on_submit():
        username='Suhasbk98'
        passwd='Gandalfthewhite123'
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

@app.route("/ssh",methods=['GET','POST'])
def ssh():
    cmds = Search()
    if cmds.validate_on_submit():
        cmd = cmds.search.data
        try:
            op = run(cmd,shell=True,stdout=PIPE,stderr=PIPE,input=b'0\nexit\n0')
            if op.stderr:
                raise ValueError
            else:
                data = op.stdout.decode('utf-8')
                return render_template("commands.html",data=data)
        except ValueError:
            flash("That command did not run successfully","info")
            return redirect(url_for('files'))
    return render_template("home.html",form=cmds,title="Enter the commands below : ")

@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = app.config['UPLOAD_FOLDER']
    return send_from_directory(directory=uploads, filename=filename, as_attachment=True)

@app.route("/test",methods=['GET','POST'])
def test():
    return render_template("test.html")

@app.route("/r")
def refresh():
    db.drop_all()
    db.create_all()
    return redirect(url_for('home'))
