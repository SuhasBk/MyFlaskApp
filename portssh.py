#!/usr/bin/python3
import os
from subprocess import call
import webbrowser
call("bash -c 'ssh -R hyperbyte:80:localhost:5000 serveo.net'",shell=True)
