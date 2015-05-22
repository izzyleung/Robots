# -*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe
from django.contrib.auth import authenticate, login
from django.http import HttpResponseForbidden

from gre_word.models import GreWord

from lxml import etree
import hashlib
from datetime import datetime

'''
Handling Web Requests
'''
def index(request):
	return render_to_response('gre_word/index.html')

def word(request):
	if request.GET:
		result = route_label(request.GET['label'])
		return HttpResponse(result) if result else HttpResponseRedirect("/")
	else:
		return HttpResponseRedirect("/")

def route_label(label, channel='default'):
	if label:
		label = label.split(" ")[0].lower()
	else:
		return ''

	if not label:
		return ''
	else:
		try:
			word = GreWord.objects.get(label=label)
			definition = word.get_definition(channel)
			if channel == 'weixin':
				return definition
			elif channel == 'default':
				word_id = word.word_id
				prev_url, next_url = None, None

				if word_id != 0:
					prev_url = '/word/?label=%s' % GreWord.objects.get(word_id=word_id - 1).label

				if word_id != GreWord.word_range - 1:
					next_url = '/word/?label=%s' % GreWord.objects.get(word_id=word_id + 1).label

				return render_to_response('gre_word/word_detail.html', {
					'definition': mark_safe(definition),
					'prev_url': prev_url,
					'next_url': next_url,
				})
			else:
				return ''
		except ObjectDoesNotExist, e:
			word_not_found_msg = GreWord.not_found_msg(label, channel)
			return word_not_found_msg if channel == 'weixin' else render_to_response('gre_word/word_detail.html', {
				'definition': mark_safe(word_not_found_msg),
			})

def words(request):
	all_words = GreWord.objects.all()

	from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

	paginator = Paginator(all_words, 20)
	page = request.GET.get('page')

	try:
		words = paginator.page(page)
	except PageNotAnInteger:
		words = paginator.page(1)
	except EmptyPage:
		words = paginator.page(paginator.num_pages)

	return render_to_response('gre_word/words.html', {
		'words': words,
	})

def alphabetical(request, letter):
	letter = letter.lower()
	letter_words = GreWord.objects.filter(label__istartswith=letter)

	from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

	paginator = Paginator(letter_words, 20)
	page = request.GET.get('page')

	try:
		words = paginator.page(page)
	except PageNotAnInteger:
		words = paginator.page(1)
	except EmptyPage:
		words = paginator.page(paginator.num_pages)
	return render_to_response('gre_word/alphabetical.html', {
		'words': words,
		'letter': letter.upper(),
		'next_letter': chr(ord(letter) + 1) if letter != 'z' else None,
		'prev_letter': chr(ord(letter) - 1) if letter != 'a' else None,
	})

def lists(request):
	return render_to_response('gre_word/lists.html', {'list_range': range(1, 32)})

def list(request, list_id):
	list_id = int(list_id)
	if int(list_id) in range(1, 32):
		unit_range = range(1, 9) if list_id == 31 else range(1, 11)
		has_next = list_id != 31
		has_prev = list_id != 1

		return render_to_response('gre_word/list.html', {
			'unit_range': unit_range,
			'list_id': list_id,
			'has_prev': has_prev,
			'has_next': has_next,
		})
	else:
		return HttpResponseForbidden()

def unit(request, list_id, unit_id):
	list_id, unit_id = int(list_id), int(unit_id)
	if check_param(list_id, unit_id):
		prev_url, next_url = None, None
		if list_id != 1 or unit_id != 1:
			prev_url = jump_unit(list_id, unit_id, 'prev')

		if list_id != 31 or unit_id != 8:
			next_url = jump_unit(list_id, unit_id, 'next')

		return render_to_response('gre_word/unit.html', {
			'is_unit': True,
			'list_id': list_id,
			'unit_id': unit_id,
			'words':  GreWord.objects.filter(list_id = list_id, unit_id = unit_id),
			'prev_url': prev_url,
			'next_url': next_url,
		})
	else:
		return HttpResponseForbidden()

def check_param(list_id, unit_id):
	if list_id in range(1, 31):
		return unit_id in range(1, 11)
	elif list_id == 31:
		return unit_id in range(1, 9)
	else:
		return False

def jump_unit(list_id, unit_id, label):
	if label == 'next':
		off_set = 1
	elif label == 'prev':
		off_set = -1
	else:
		return "/"

	return '/list/%s/unit/%s' % compute_unit((list_id - 1) * 10 + (unit_id - 1) + off_set)

def compute_unit(num):
	list_id = num / 10 + 1
	unit_id = (num - (list_id - 1) * 10) + 1

	return (str(list_id), str(unit_id))

'''
Sending Weibo
'''
# Sometimes publishing Weibo will fail, presumably due to large image
# Check the status every minute: if publishing fails, publish Weibo status again
def pub_weibo(request):
	import sae.kvdb
	import calendar
	import time
	kv = sae.kvdb.KVClient()
	minute_now = datetime.now().minute
	time_now_epoch = calendar.timegm(time.gmtime())
	last_pub_time = kv.get('last_pub_time')

	hour_now = datetime.now().hour
	if hour_now > 0 and hour_now < 7:
		return HttpResponse("Time to Sleep :-D")
	elif (minute_now % 10 == 0) or (time_now_epoch - last_pub_time >= 600):
		from random import randrange
		send_weibo(GreWord.objects.get(word_id=randrange(GreWord.word_range)))
		kv.set('last_pub_time', calendar.timegm(time.gmtime()))
		return HttpResponse("Pub Done!")
	else:
		return HttpResponse("Nope")

def send_weibo(word):
	import os
	os.environ['REMOTE_ADDR'] = "28.35.201.50"

	auth_url = 'https://api.weibo.com/2/oauth2/access_token'

	from weibo import APIClient
	import requests, json
	import credential

	result = json.loads(requests.post(auth_url, data=credential.login_data).text)
	access_token = result['access_token']
	expires_in = result['expires_in']

	client = APIClient(app_key=credential.login_data['client_id'],
	 app_secret=credential.login_data['client_secret'])
	client.set_access_token(access_token, expires_in)

	client.statuses.upload.post(status=word.gen_weibo_text(), pic=word.gen_weibo_image())

'''
Handling WeChat Requests
'''
@csrf_exempt
def weixin(request):
	if request.method == 'GET':
		return HttpResponse(check_signature(request), content_type="text/plain")
	elif request.method == 'POST':
		return HttpResponse(reply_definition(request), content_type="application/xml")
	else:
		return None

def check_signature(request):
	token = "izzy"
	signature = request.GET.get("signature")
	timestamp = request.GET.get("timestamp")
	nonce = request.GET.get("nonce")
	echostr = request.GET.get("echostr")
	signature_tmp = [token,timestamp,nonce]

	signature_tmp.sort()
	signature_tmp = ''.join(signature_tmp)
	signature_tmp = hashlib.sha1(signature_tmp).hexdigest()
	if signature_tmp == signature:
		return echostr

def reply_definition(request):
	xmlstr = smart_str(request.body)
	xml = etree.fromstring(xmlstr)
	ToUserName = xml.find('ToUserName').text
	FromUserName = xml.find('FromUserName').text
	MsgType = xml.find('MsgType').text

	if MsgType == 'event' and xml.find('Event').text == "subscribe":
		return render_to_response('gre_word/reply.xml', {
			'to_user_name': FromUserName,
			'content': "欢迎关注再要你命机器人，它是你杀 G 路上的伴侣～回复任意单词即可查看其释义与其在 GRE 中的考点。:-D",
		})
	else:
		xml_content = xml.find("Content")
		Content = " " if xml_content == None else " " if xml_content.text == "" else xml_content.text

		return render_to_response('gre_word/reply.xml', {
			'to_user_name': FromUserName,
			'content': route_label(Content, channel="weixin"),
		})
