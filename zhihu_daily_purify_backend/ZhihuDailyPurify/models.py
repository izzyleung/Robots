from bs4 import BeautifulSoup
from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime
from configparser import ConfigParser
from pytz import timezone
from aiohttp import ClientSession

ZHIHU_DAILY_URL = 'http://news-at.zhihu.com/api/4/news/'
ZHIHU_DAILY_BEFORE_URL = ZHIHU_DAILY_URL + 'before/'


class Story:
    def __init__(self, index=None, date=None, story_id=None, daily_title=None, thumbnail_url=None, document=None):
        self.index = index
        self.date = date
        self.story_id = story_id
        self.daily_title = daily_title
        self.thumbnail_url = thumbnail_url
        self.document = document

    @staticmethod
    async def stories_of_date(date):
        with ClientSession() as session:
            response = await session.get(ZHIHU_DAILY_BEFORE_URL + date)
            json_response = await response.json()

            return await Story.stories(session, json_response, date)

    @staticmethod
    async def stories(session, json, date):
        stories = json['stories']
        result = []

        for index, s in enumerate(stories):
            story = Story(index=index, date=date,
                          story_id=s['id'], daily_title=s['title'],
                          thumbnail_url=Story.get_thumbnail_url(s),
                          document=await Story.get_document(session, s))
            result.append(story)

        return result

    @staticmethod
    def get_thumbnail_url(story):
        if 'images' in story and len(story['images']) != 0:
            return story['images'][0]
        else:
            return None

    @staticmethod
    async def get_document(session, story):
        response = await session.get(ZHIHU_DAILY_URL + str(story['id']))
        json_response = await response.json()

        if 'body' in json_response:
            return BeautifulSoup(json_response['body'], 'lxml')
        else:
            return None


class Question:
    ZHIHU_QUESTION_LINK_PREFIX = 'http://www.zhihu.com/question/'

    def __init__(self, title=None, url=None):
        self.title = title
        self.url = url

    def is_valid(self):
        return self.url is not None and self.url.startswith(self.ZHIHU_QUESTION_LINK_PREFIX)


class DailyNews:
    def __init__(self, index=None, date=None, daily_title=None, thumbnail_url=None, questions=None):
        self.index = index
        self.date = date
        self.daily_title = daily_title
        self.thumbnail_url = thumbnail_url
        self.questions = questions

    @staticmethod
    def from_story(story):
        if not story.document:
            return None

        news = DailyNews(index=story.index, date=story.date,
                         daily_title=story.daily_title, thumbnail_url=story.thumbnail_url,
                         questions=[])

        question_elements = DailyNews.get_question_elements(story.document)
        for question_element in question_elements:
            question_url = DailyNews.get_question_url(question_element)
            question_title = DailyNews.get_question_title(question_element)

            # Make sure that the question's title is not null.
            question_title = question_title or story.daily_title

            question = Question(title=question_title.strip(), url=question_url)
            news.questions.append(question)

        if all(question.is_valid() for question in news.questions):
            return news
        else:
            return None

    @staticmethod
    def get_question_title(question_element):
        question_title_elements = DailyNews.get_question_title_elements(question_element)
        if question_title_elements and question_title_elements.text:
            return question_title_elements.text
        else:
            return None

    @staticmethod
    def get_question_elements(document):
        return document.find_all('div', attrs={'class': 'question'})

    @staticmethod
    def get_question_title_elements(question_element):
        return question_element.find('h2', attrs={'class': 'question-title'})

    @staticmethod
    def get_question_url(question_element):
        view_more_element = question_element.find('div', attrs={'class': 'view-more'})

        if view_more_element:
            return view_more_element.find('a')['href']
        else:
            return None

    def to_dict(self):
        return {
            'index': self.index,
            'date': self.date,
            'dailyTitle': self.daily_title,
            'thumbnailUrl': self.thumbnail_url,
            'questions': [question.__dict__ for question in self.questions],
        }


class DailyNewsCollection:
    @staticmethod
    def jsonify_result(result):
        return {'news': result}

    @staticmethod
    async def search_by_keyword(keyword):
        if keyword is None:
            return DailyNewsCollection.jsonify_result([])

        criteria = {
            "$or": [{"dailyTitle": DailyNewsCollection.criteria_keyword_ignore_case(keyword)},
                    {"questions.title": DailyNewsCollection.criteria_keyword_ignore_case(keyword)}]
        }

        return DailyNewsCollection.jsonify_result(await DailyNewsCollection.query_mongo_collection(criteria))

    @staticmethod
    def criteria_keyword_ignore_case(keyword):
        return {
            "$regex": ".*" + keyword + ".*",
            "$options": "i",
        }

    @staticmethod
    async def of_date(date):
        return DailyNewsCollection.jsonify_result(await DailyNewsCollection._of_date(date))

    @staticmethod
    async def _of_date(date):
        d = _DateTime.parse_date(date)

        if d is None:
            # Parameter format invalid
            return []

        if _DateTime.is_date_before_birthday(d):
            return []
        elif _DateTime.is_date_after_current_date_shanghai(d):
            # Return the latest result in Collection
            return await DailyNewsCollection.get_news_list(datetime.strftime(_DateTime.get_current_time_shanghai(),
                                                                             _DateTime.DATE_FORMAT))
        else:
            # Parameter in range
            return await DailyNewsCollection.get_news_list(date)

    @staticmethod
    async def get_news_list(date):
        if not await DailyNewsCollection.is_record_in_mongo_collection(date):
            await DailyNewsCollection.get_news_list_from_zhihu_and_save_to_mongo(date)
        return await DailyNewsCollection.get_news_list_from_mongo_collection(date)

    @staticmethod
    async def get_news_list_from_zhihu_and_save_to_mongo(date):
        news_list = await DailyNewsCollection.get_news_list_from_zhihu(date)
        await DailyNewsCollection.save_to_mongo([news.to_dict() for news in news_list])

    @staticmethod
    async def get_news_list_from_zhihu(date):
        stories = await Story.stories_of_date(date)
        return [DailyNews.from_story(story) for story in stories if DailyNews.from_story(story) is not None]

    @staticmethod
    async def save_to_mongo(news_list):
        news_collection = await DailyNewsCollection.get_mongo_collection()
        news_collection.insert_many(news_list)

    @staticmethod
    async def is_record_in_mongo_collection(date):
        collection = await DailyNewsCollection.get_mongo_collection()
        return collection.find({'date': date}).count() > 0

    @staticmethod
    async def get_news_list_from_mongo_collection(date):
        return await DailyNewsCollection.query_mongo_collection({'date': date})

    @staticmethod
    async def query_mongo_collection(criteria):
        collection = await DailyNewsCollection.get_mongo_collection()
        search_result = collection \
            .find(criteria, {'_id': False, 'index': False}) \
            .sort([('date', DESCENDING), ('index', ASCENDING)])
        return [r for r in search_result]

    @staticmethod
    async def get_mongo_collection():
        config = await DailyNewsCollection.get_config()

        client = MongoClient('mongodb://%s:%s@%s/%s' % await DailyNewsCollection.get_database_connection_info(config))
        db = client.get_default_database()

        collection_name = await DailyNewsCollection.get_mongo_collection_name(config)
        return db[collection_name]

    @staticmethod
    async def get_database_connection_info(config):
        uri = config.get('Database', 'URI')
        user = config.get('Credential', 'User')
        password = config.get('Credential', 'Password')
        database_name = config.get('Database', 'Name')

        return user, password, uri, database_name

    @staticmethod
    async def get_mongo_collection_name(config):
        return config.get('Database', 'Collection')

    @staticmethod
    async def get_config():
        config = ConfigParser()
        config.read('database.ini')
        return config


class _DateTime:
    BIRTHDAY = datetime(2013, 5, 19)
    DATE_FORMAT = '%Y%m%d'

    @staticmethod
    def parse_date(date):
        try:
            d = datetime.strptime(date, _DateTime.DATE_FORMAT)
            return _DateTime.convert_time_to_shanghai(d)
        except ValueError:
            return None

    @staticmethod
    def is_date_before_birthday(d):
        return d <= _DateTime.convert_time_to_shanghai(_DateTime.BIRTHDAY)

    @staticmethod
    def is_date_after_current_date_shanghai(d):
        return d > _DateTime.get_current_time_shanghai()

    @staticmethod
    def get_gmt_timezone():
        return timezone('GMT')

    @staticmethod
    def get_shanghai_timezone():
        return timezone('Asia/Shanghai')

    @staticmethod
    def convert_time_to_shanghai(date):
        return _DateTime.get_shanghai_timezone().localize(date)

    @staticmethod
    def get_current_time_shanghai():
        shanghai = _DateTime.get_shanghai_timezone()
        gmt = _DateTime.get_gmt_timezone()
        now_gmt = gmt.localize(datetime.now())
        return now_gmt.astimezone(shanghai)
