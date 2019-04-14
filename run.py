#!/usr/bin/python3

from myflask import app
import webbrowser

if __name__=='__main__':
    app.run(host='localhost',debug=True,threaded=True)
