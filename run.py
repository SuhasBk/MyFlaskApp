#!/usr/bin/env python

from myflask import app
import webbrowser

if __name__=='__main__':
    webbrowser.open("http://localhost:5000")
    app.run(host='localhost',debug=True,threaded=True)
