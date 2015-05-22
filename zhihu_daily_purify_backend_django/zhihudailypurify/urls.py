# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'zhihudailypurify.views.home', name='home'),
    # url(r'^zhihudailypurify/', include('zhihudailypurify.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'daily_news.views.index'),
    url(r'^raw/(?P<date_string>\d+)/$', 'daily_news.views.raw', name='date_string'),
    url(r'^search/(?P<key_word>[\w|\W]+)/$', 'daily_news.views.search', name='key_word'),
)
