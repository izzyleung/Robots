# -*- coding: utf-8 -*-

from django.db import models

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from PIL import Image, ImageDraw, ImageFont
import StringIO
import math

class GreWord(models.Model):
	word_id = models.IntegerField()
	label = models.CharField(max_length=30)
	phonetic = models.CharField(max_length=30)
	detail = models.TextField()
	list_id = models.IntegerField()
	unit_id = models.IntegerField()

	word_range = 3073

	def __str__(self):
		return self.label

	class Meta:
		verbose_name = 'GRE Word'
		verbose_name_plural = 'GRE Words'

	def get_definition(self, channel='default'):
		definition =  str(self.label
			+ " " + self.phonetic
			+ "\n" + self.detail)
		if channel == 'weixin':
			return '\n'.join(definition.split('♠'))
		elif channel == 'default':
			return '<br>'.join(definition.replace('\n', "<br>").split('♠'))
		else:
			return ''

	@staticmethod
	def not_found_msg(label, channel='default'):
		base_str = '《再要你命3000》书中未出现该词，您可参考韦式词典中该词的释义：'
		if channel == 'default':
			return base_str + '<a href="http://www.merriam-webster.com/dictionary/%s">%s</a>' % (label, label)
		elif channel == 'weixin':
			return base_str + "http://www.merriam-webster.com/dictionary/%s" % label
		else:
			return ""

	def gen_weibo_text(self):
		return str(self.label)\
		+ " " + str(self.phonetic)\
		+ " 来自韦式词典的释义：http://www.merriam-webster.com/dictionary/"\
		+ str(self.label)\
		+ " 来自《再要你命 3000》书中的 GRE 考点请见图片 >>> "

	def gen_weibo_image(self):
		text = ""
		for line in str(" " + self.detail).split('♠'):
			text = text + line + "\n"

		# Configurations:
		adtexts = [u'---------------', u'欢迎关注微信 GRE_Machine']
		textcolor = "#000000"
		adcolor = "#FF0000"
		line_len = 43

		# Build rich text for ads
		ad = []
		for adtext in adtexts:
			ad += [(adtext.encode('utf-8'), adcolor)]

		# Wrap line for text
		#   Special treated Chinese characters
		#   Workaround By Felix Yan - 20110508
		wraptext = [""]

		max_len = 0

		for line in text.split("\n"):
			l = 0
			for word in line.split(None):
				if ord(word[0]) > 127:
					for i in word.decode('utf-8'):
						fi = i.encode('utf-8')
						delta = len(i) * 1.73
						if math.ceil(l) + delta > line_len:
							wraptext += [fi]

							if l > max_len:
								max_len = l

							l = delta
						else:
							wraptext[-1] += fi
							l += delta
				else:
					delta = len(word)
					if math.ceil(l) + delta > line_len:
						wraptext += [word]

						if l > max_len:
								max_len = l

						l = delta
						l = l + 1
					else:
						wraptext[-1] += word
						l += delta
						l = l + 1

				wraptext[-1] += " "

			wraptext += [""]

		# Format wrapped lines to rich text
		wrap = [(text, textcolor) for text in wraptext]
		wrap += ad

		# Draw picture
		i = Image.new("RGB", (450, len(wrap) * 18 + 5), "#FFFFFF")
		d = ImageDraw.Draw(i)
		f = ImageFont.truetype("microhei.ttc", 18)

		for num, (text, color) in enumerate(wrap):
			d.text((3, 18 * num + 1), unicode(text,'utf-8'), font = f, fill = color)

		width = 0
		for x in wraptext:
			word_width, word_height = d.textsize(x.decode('utf-8'), font=f)
			if word_width > width:
				width = word_width

		# Save and return an image as IO stream
		# since we cannot save an image to storage on Sina App Engine
		io = StringIO.StringIO()
		i.crop((0, 0, width + 5, len(wrap) * 18 + 5)).save(io, format='PNG')

		return io
