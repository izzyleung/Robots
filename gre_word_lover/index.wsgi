# coding: UTF-8
# -*- coding: utf-8 -*-

import sae
import os
import sys
os.environ['REMOTE_ADDR'] = "219.139.232.193"

app_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(app_root, 'virtualenv.bundle'))

from grewordlover import wsgi

application = sae.create_wsgi_app(wsgi.application)
