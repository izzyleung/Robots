import sae
import os
import sys

app_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(app_root, 'virtualenv.bundle'))

from quora_show import app

application = sae.create_wsgi_app(app)
