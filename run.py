#!/usr/local/bin/python3
from myflask import app
import sys
import os

if __name__=='__main__':
    try:
        ip = sys.argv[1]
        port = sys.argv[2]
    except IndexError:
        ip = "localhost"
        port = 5000
    
    debug = True if os.environ.get("HIDDEN_ID") == 'BATMAN' else False

    app.run(host=ip,debug=debug,port=port)
