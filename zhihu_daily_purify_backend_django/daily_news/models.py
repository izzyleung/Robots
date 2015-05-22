# coding=utf-8

from django.db import models
from django.core.exceptions import ValidationError
from bs4 import BeautifulSoup
import json, time, requests

import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class DailyNews(models.Model):
    date = models.CharField(max_length=8)
    content = models.TextField()

    class Meta:
        verbose_name_plural = "DailyNews"

    def __str__(self):
        return self.date

    def download_content(self):
        try:
            time.strptime(str(self.date), '%Y%m%d')
        except ValueError, e:
            return None

        json_news = requests.get('http://news-at.zhihu.com/api/3/news/before/%s' % self.date).json()['stories']
        news_list = []

        for n in json_news:
            news = {
                'isMulti': False,
                'dailyTitle': n['title'],
                'questionTitle': '',
                'questionUrl': '',
                'questionTitleList': [],
                'questionUrlList': [],
                'thumbnailUrl': n['images'][0] if 'images' in n and len(n['images']) != 0 else None
            }
            news_detail = requests.get("http://news-at.zhihu.com/api/3/news/%s" % n['id']).json()

            if news_detail.has_key('body'):
                bs = BeautifulSoup(news_detail['body'])
                view_more = bs.find_all('div', {'class': 'view-more'})
                if len(view_more) > 1:
                    news['isMulti'] = True
                    should_append = True

                    for node in view_more:
                        if node.find('a'):
                            if node.find('a').text == u'查看知乎讨论':
                                news['questionUrlList'].append(node.find('a')['href'])
                            else:
                                should_append = False
                        else:
                            continue    

                    for node in bs.find_all('h2'):
                        title = node.get_text() if node.get_text() != "" else n['title']
                        news['questionTitleList'].append(title)

                    if should_append:
                        news_list.append(news)
                elif len(view_more) == 1:
                    question_element = (bs.find('div', {'class': 'view-more'})).find('a')
                    if question_element.text == u'查看知乎讨论':
                        news['questionUrl'] = question_element['href']

                        title = bs.find('h2').get_text()
                        news['questionTitle'] = title if title != "" else n['title']

                        news_list.append(news)

        return json.dumps(news_list, ensure_ascii=False).encode('utf-8')

    def clean(self):
        if not self.date or not self.content:
            raise ValidationError("Content cannot be null")
        else:
            try:
                time.strptime(str(self.date), '%Y%m%d')
            except ValueError, e:
                raise ValidationError("Date illegal")