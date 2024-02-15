#!/usr/local/bin/python3
import sys
import os
from myflask import app
from myflask import routes
from myflask.app_scheduler import AppScheduler

if __name__=='__main__':
    try:
        ip = sys.argv[1]
        port = sys.argv[2]
    except IndexError:
        ip = "0.0.0.0"
        port = 8000
    
    app_scheduler = AppScheduler()
    app_scheduler.start()
    
    app.run(host=ip,debug=False,port=port)
