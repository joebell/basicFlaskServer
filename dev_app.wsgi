#! /usr/local/anaconda3/bin/python

import sys
sys.path.insert(0, '/var/www/dev')
sys.path.append('/usr/local/anaconda3/bin/')
from server import app as application
