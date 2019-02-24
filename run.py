#!/usr/bin/env python

from myflask import app

if __name__=='__main__':
    app.run(host='localhost',debug=True,threaded=True)
