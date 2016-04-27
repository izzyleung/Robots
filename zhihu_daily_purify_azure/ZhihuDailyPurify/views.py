# -*- coding: utf-8 -*-

import json

from flask import Response, request

from ZhihuDailyPurify import app
from daily_news import news_of, search_news_by, jsonify_result


@app.route('/')
def index():
    return 'index'


@app.route('/news/<date>')
def news(date):
    return json_response(news_of(date))


@app.route('/search/')
def search():
    keyword = request.args.get('q', None)
    if keyword:
        return json_response(search_news_by(keyword))
    else:
        return json_response(jsonify_result([]))


def json_response(data):
    return Response(response=json_dump(data), content_type='application/json; charset=utf-8')


def json_dump(data):
    return json.dumps(data, ensure_ascii=False).encode('utf-8')
