#!/usr/bin/python3

from myflask import app
import webbrowser
#webbrowser.open("http://localhost:5000")
if __name__=='__main__':
    app.run(host='localhost',debug=True,threaded=True)
