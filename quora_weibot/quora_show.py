# coding=utf-8

import MySQLdb
import requests
from _mysql_exceptions import OperationalError
from flask import Flask, g
from time import sleep

import credential

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
app.config['DEBUG'] = True

from os import environ

debug = not environ.get('APP_NAME', '')
if debug:
    MYSQL_DB = credential.MYSQL_DB
    MYSQL_USER = credential.MYSQL_USER
    MYSQL_PASS = credential.MYSQL_PASS
    MYSQL_HOST_M = credential.MYSQL_HOST_M
    MYSQL_HOST_S = credential.MYSQL_HOST_S
    MYSQL_PORT = credential.MYSQL_PORT
else:
    import sae.const

    MYSQL_DB = sae.const.MYSQL_DB
    MYSQL_USER = sae.const.MYSQL_USER
    MYSQL_PASS = sae.const.MYSQL_PASS
    MYSQL_HOST_M = sae.const.MYSQL_HOST
    MYSQL_HOST_S = sae.const.MYSQL_HOST_S
    MYSQL_PORT = sae.const.MYSQL_PORT


@app.before_request
def before_request():
    g.db = MySQLdb.connect(MYSQL_HOST_M, MYSQL_USER, MYSQL_PASS, MYSQL_DB,
                           port=int(MYSQL_PORT), charset='utf8')


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'): g.db.close()


@app.route('/')
def index():
    return 'How I wish, how I wish you were here.'


@app.route('/cron/pub_weibo')
def pub_weibo():
    pub_and_save_weibos()
    return 'Got it!'


def get_tweets_list():
    return [Status(t['twitter_id'], t['status_text'], t['urls'])
            for t in requests.get('http://tweetsfetch.herokuapp.com/timeline/Quora').json()]


def filter_not_published():
    return [t for t in get_tweets_list() if not t.is_record_exist()]


def pub_and_save_weibos():
    for t in reversed(filter_not_published()):
        t.pub_weibo()
        t.save()
        sleep(4)


class Status(object):
    def __init__(self, twitter_id, status_text, urls):
        super(Status, self).__init__()
        self.twitter_id = twitter_id
        self.status_text = status_text
        self.urls = urls

    def __repr__(self):
        return "<Status: " + self.status_text + ">"

    def is_record_exist(self):
        return g.db.cursor().execute('SELECT * FROM tweets WHERE twitter_id = %s' % self.twitter_id)

    # Replace full url(s) with shortened url(s)
    def prepare_weibo_status(self):
        if self.urls:
            status = self.status_text
            for url in self.urls:
                short_url = requests.get('https://api.weibo.com/2/short_url/shorten.json',
                                         params={'source': '2323547071', 'url_long': url}).json()['urls'][0][
                    'url_short']
                status = status.replace(url, short_url)
            return status
        else:
            return self.status_text

    def pub_weibo(self):
        import os

        os.environ['REMOTE_ADDR'] = '28.35.201.50'

        send_weibo_data = {
            'access_token': requests.post('https://api.weibo.com/2/oauth2/access_token',
                                          data=credential.login_data).json()['access_token'],
            'status': self.prepare_weibo_status()
        }

        requests.post('https://api.weibo.com/2/statuses/update.json', data=send_weibo_data)

    def save(self):
        try:
            g.db.cursor().execute('''INSERT INTO tweets (twitter_id, status_text) VALUES (%s, %s);''',
                                  (self.twitter_id, self.status_text))
            g.db.commit()
        except OperationalError:
            g.db.rollback()


if __name__ == '__main__':
    app.run()
