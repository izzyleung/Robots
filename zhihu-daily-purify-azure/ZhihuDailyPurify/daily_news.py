# -*- coding: utf-8 -*-

import pytz
import pymongo
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
from ConfigParser import ConfigParser

ZHIHU_DAILY_URL = 'http://news-at.zhihu.com/api/4/news/'
ZHIHU_DAILY_BEFORE_URL = ZHIHU_DAILY_URL + 'before/'
ZHIHU_QUESTION_LINK_PREFIX = 'http://www.zhihu.com/question/'

BIRTHDAY = datetime(2013, 5, 19)
DATE_FORMAT = '%Y%m%d'


def news_of(date):
    return jsonify_result(news_list_of(date))


def search_news_by(keyword):
    criteria = {
        "$or": [{"dailyTitle": criteria_keyword_ignore_case(keyword)},
                {"questions.title": criteria_keyword_ignore_case(keyword)}]
    }
    return jsonify_result(query_collection(criteria))


def criteria_keyword_ignore_case(keyword):
    return {
        "$regex": ".*" + keyword + ".*",
        "$options": "i",
    }


def jsonify_result(result):
    return {'news': result}


def news_list_of(date):
    d = parse_date(date)

    if d is None:
        # Parameter format invalid
        return []

    if is_date_before_birthday(d):
        return []
    elif is_date_after_current_date_shanghai(d):
        # Return the latest result in Collection
        return get_news_list(datetime.strftime(get_current_time_shanghai(), DATE_FORMAT))
    else:
        # Parameter in range
        return get_news_list(date)


def get_news_list(date):
    if not is_record_in_collection(date):
        get_news_list_from_zhihu_and_save_to_mongo(date)
    return get_news_list_from_collection(date)


def is_record_in_collection(date):
    collection = get_daily_news_collection()
    return collection.find({'date': date}).count() > 0


def get_news_list_from_collection(date):
    return query_collection({'date': date})


def query_collection(criteria):
    collection = get_daily_news_collection()
    search_result = collection.find(criteria, {'_id': False, 'index': False}).sort(
        [('date', pymongo.DESCENDING), ('index', pymongo.ASCENDING)])
    return [r for r in search_result]


def get_news_list_from_zhihu_and_save_to_mongo(date):
    news_list = get_news_list_from_zhihu(date)
    save_to_mongo(news_list)


def get_news_list_from_zhihu(date):
    raw_news_list = [story_to_raw_news(story) for story in get_stories(date)]
    result = [process_raw_news(raw_news) for raw_news in raw_news_list]

    return [r for r in result if r is not None]


def story_to_raw_news(story):
    return {
        'index': story['index'],
        'date': story['date'],
        'dailyTitle': story['dailyTitle'],
        'thumbnailUrl': story['thumbnailUrl'],
        'document': story['document'],
    }


def process_raw_news(raw_news):
    if not raw_news['document']:
        return None

    news = {
        'index': raw_news['index'],
        'date': raw_news['date'],
        'dailyTitle': raw_news['dailyTitle'],
        'thumbnailUrl': raw_news['thumbnailUrl'],
        'questions': [],
    }

    question_elements = get_question_elements(raw_news['document'])
    for question_element in question_elements:
        question_url = get_question_url(question_element)
        question_title = get_question_title(question_element)

        # Make sure that the question's title is not null.
        question_title = question_title or get_question_title_from(question_url) or raw_news['dailyTitle']

        question = {
            'title': question_title.strip(),
            'url': question_url,
        }
        news['questions'].append(question)

    if all(is_url_to_zhihu(question['url']) for question in news['questions']):
        return news
    else:
        return None


def get_question_elements(document):
    return document.find_all('div', attrs={'class': 'question'})


def get_question_title(question_element):
    question_title_elements = get_question_title_elements(question_element)
    if question_title_elements and question_title_elements.text:
        return question_title_elements.text
    else:
        return None


def get_question_title_elements(question_element):
    return question_element.find('h2', attrs={'class': 'question-title'})


def get_question_url(question_element):
    view_more_element = question_element.find('div', attrs={'class': 'view-more'})

    if view_more_element:
        return view_more_element.find('a')['href']
    else:
        return None


def get_question_title_from(question_url):
    if question_url is None:
        return None

    html = requests.get(question_url)
    soup = BeautifulSoup(html.text, 'lxml')
    h2_element = soup.find('h2')
    return h2_element.text if h2_element is not None else None


def is_url_to_zhihu(link):
    return link is not None and link.startswith(ZHIHU_QUESTION_LINK_PREFIX)


def get_stories(date):
    stories = requests.get(ZHIHU_DAILY_BEFORE_URL + date).json()['stories']
    return [story_info(index, date, story) for index, story in enumerate(stories)]


def story_info(index, date, story):
    return {
        'index': index,
        'date': date,
        'storyId': story['id'],
        'dailyTitle': story['title'].strip(),
        'thumbnailUrl': get_thumbnail_url(story),
        'document': get_document(story),
    }


def get_thumbnail_url(story):
    if 'images' in story and len(story['images']) != 0:
        return story['images'][0]
    else:
        return None


def get_document(story):
    info = requests.get(ZHIHU_DAILY_URL + str(story['id'])).json()
    if 'body' in info:
        return BeautifulSoup(info['body'], 'lxml')
    else:
        return None


def save_to_mongo(news_list):
    daily_news = get_daily_news_collection()
    daily_news.insert_many(news_list)


def get_daily_news_collection():
    config = get_config()

    client = MongoClient('mongodb://%s:%s@%s/%s' % get_database_connection_info(config))
    db = client.get_default_database()

    collection_name = get_collection_name(config)
    return db[collection_name]


def get_database_connection_info(config):
    uri = config.get('Database', 'URI')
    user = config.get('Credential', 'User')
    password = config.get('Credential', 'Password')
    database_name = config.get('Database', 'Name')

    return user, password, uri, database_name


def get_collection_name(config):
    return config.get('Database', 'Collection')


def get_config():
    config = ConfigParser()
    config.read('database.ini')
    return config


def parse_date(date):
    try:
        d = datetime.strptime(date, DATE_FORMAT)
        return convert_time_to_shanghai(d)
    except ValueError:
        return None


def is_date_before_birthday(d):
    return d <= convert_time_to_shanghai(BIRTHDAY)


def is_date_after_current_date_shanghai(d):
    return d > get_current_time_shanghai()


def get_gmt_timezone():
    return pytz.timezone('GMT')


def get_shanghai_timezone():
    return pytz.timezone('Asia/Shanghai')


def convert_time_to_shanghai(date):
    return get_shanghai_timezone().localize(date)


def get_current_time_shanghai():
    shanghai = get_shanghai_timezone()
    gmt = get_gmt_timezone()
    now_gmt = gmt.localize(datetime.now())
    return now_gmt.astimezone(shanghai)
