#!/usr/bin/python3

from myflask import app
if __name__=='__main__':
    app.run(host='192.168.0.101',debug=True,threaded=True)
