from flask import render_template,url_for,flash,redirect,request,abort,jsonify
from flask_ask import question,statement,session,delegate
from myflask.forms import Search,NewHandle,LoginForm
from myflask.models import Nice,Twitter
from flask import Flask
from myflask import app,db,ask
import os,random,re,time
import requests
from bs4 import BeautifulSoup

#ALEXA!!!!
@app.route('/alexa')
def alexa():
    return render_template('alexa.html')

@ask.launch
def start_skill():
    welcome = "Hello boss! Hyperbyte is online. I can tell you a famous quote. I can also give you meaning of a word. I can also mimic you if you want me to. I can also give you some knock knock jokes!"
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
        l = s.findAll('a',attrs={'aria-hidden':'true'})

        reg = []
        for i in l:
            if('googleadservices' not in i.get("href") and 'https' not in i.get('href')):
                reg.append('http://youtube.com/embed'+i.get("href").replace('watch?v=','')+"?cc_load_policy=1&rel=0")

        vids=set(reg[:20])

        for i in vids:
            new = Nice(url=str(i))
            db.session.add(new)
            db.session.commit()
        links = Nice.query.all()
        return render_template('vids.html',posts=links,title='YouTube')
    return render_template('home.html',title='YouTube',form=f)

@app.route("/boom",methods=['GET','POST'])
def boom():
    try:
        db.drop_all()
        db.create_all()
    except:
        pass
    form = Search()
    if form.validate_on_submit():
        k = form.search.data
        try:
            r=requests.get("http://xvideos.com/?k="+k)
        except:
            abort(404)
        l=BeautifulSoup(r.text,'html.parser').select('a')

        links=[]
        for i in l:
            try:
                if '/video' in i.get('href'):
                    if i.get('title')!=None:
                        links.append([i.get("title"),i.get('href')])
            except:
                pass

        for i in links[:5]:
            try:
                r1=requests.get("https://xvideos.com"+i[1])
                url=re.findall("html5player.setVideoUrlHigh\('(.*)'\);",r1.text)[0]
                vids = Nice(url=url)
                db.session.add(vids)
                db.session.commit()
            except:
                pass
        links = Nice.query.all()
        return render_template('vids.html',posts=links,title='XVideos')
    return render_template('home.html',title='Boom',form=form)

@app.route("/fap",methods=['GET','POST'])
def fap():
    try:
        db.drop_all()
        db.create_all()
    except:
        pass

    r=requests.get("https://pornhub.net/")

    a=BeautifulSoup(r.text,'html.parser').select('a')

    v=[]
    for i in a:
        if i.get("href")!=None and 'viewkey' in i.get("href"):
            key=re.findall(r'viewkey=(\w+)',i.get('href'))[0]
            url = "https://pornhub.net/embed/"+key
            v.append(url)

    for i in set(v):
        vids=Nice(url=i)
        db.session.add(vids)
        db.session.commit()

    links = Nice.query.all()
    return render_template('vids.html',posts=links,title='Videos')

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

    r=requests.get("http://c.xkcd.com/random/comic/")
    text=r.text
    data=BeautifulSoup(text,'html.parser').select('img')[1].get('src')

    img=Nice(url='http:'+data)
    db.session.add(img)
    db.session.commit()
    links = Nice.query.all()
    return render_template('vids.html',posts=links,title='XKCD WebComics')

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

@app.route('/remove_handle/<id>',methods=['GET','POST'])
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
    return render_template("home.html",form=subr)

@app.route("/files",methods=['GET','POST'])
def files():
    folder = Search()
    if folder.validate_on_submit():
        folder = folder.search.data
        try:
            files = sorted(os.listdir(folder))
            return render_template("files.html",files=files,folder=folder)
        except:
            flash("No such directory found! Try again...","info")
            return redirect(url_for('files'))
    return render_template("home.html",form=folder)

@app.route("/r")
def refresh():
    db.drop_all()
    db.create_all()
    return redirect(url_for('home'))
