#!/usr/bin/python3
from myflask import app
import sys

if __name__=='__main__':
    try:
        ip = sys.argv[1]
    except IndexError:
        ip = "localhost"
    
    app.run(host=ip,debug=True)
