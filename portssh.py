#!/usr/bin/python3
import os
from subprocess import call
call("ssh -R hyperbyte:80:localhost:5000 serveo.net",shell=True)
