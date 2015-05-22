# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from daily_news.models import DailyNews
from django.core.exceptions import ObjectDoesNotExist, ValidationError

import json
from datetime import datetime

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

def index(request):
	return render_to_response('daily_news/index.html')

def raw(request, date_string):
	try:
		date = datetime.strptime(date_string, "%Y%m%d")
		if date > datetime(2013, 5, 19) and date <= datetime(2014, 10, 13):
			try:
				news = DailyNews.objects.get(date=date_string)
				return HttpResponse(news.content)
			except ObjectDoesNotExist, e:
				news = DailyNews()
				news.date = date_string
				news.content = news.download_content()
				try:
					news.clean()
					news.save()
					return HttpResponse(news.content)
				except ValidationError, e:
					return HttpResponse("")
		elif date > datetime(2014, 10, 13):
			return HttpResponse(u"现在这个服务器已经无法获取知乎的消息，请在设置中启用 Heroku 这个加速服务器吧")
		else:
			return HttpResponse("")
	except ValueError, e:
		return HttpResponse(e)

def search(request, key_word):
	result_list = []
	for single_news in DailyNews.objects.filter(content__contains=key_word).order_by('-date'):
		for news in json.loads(single_news.content):
			if key_word in news['dailyTitle']:
				found_news = {'date': single_news.date, 'content': news}
				result_list.append(found_news)
				continue

			if news['isMulti']:
				for title in news['questionTitleList']:
					if key_word in title:
						found_news = {'date': single_news.date, 'content': news}
						result_list.append(found_news)
						break
			else:
				if key_word in news['questionTitle']:
					found_news = {'date': single_news.date, 'content': news}
					result_list.append(found_news)

	return HttpResponse(json.dumps(result_list, ensure_ascii=False).encode('utf-8'))
