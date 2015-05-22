# coding: UTF-8
# -*- coding: utf-8 -*-

import sys
import os

app_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(app_root, 'virtualenv.bundle'))

import sae
from zhihudailypurify import wsgi

application = sae.create_wsgi_app(wsgi.application)
