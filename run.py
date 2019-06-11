#!/usr/bin/python3

from myflask import socketio,app

if __name__=='__main__':
    socketio.run(app,host='localhost',debug=True)
