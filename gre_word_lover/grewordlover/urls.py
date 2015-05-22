from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gre_word_lover.views.home', name='home'),
    # url(r'^gre_word_lover/', include('gre_word_lover.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'gre_word.views.index'),
    url(r'^lists/$', 'gre_word.views.lists'),
    url(r'^list/(?P<list_id>\d+)/$', 'gre_word.views.list', name='list_id'),
    url(r'^list/(?P<list_id>\d+)/unit/(?P<unit_id>\d+)/$', 'gre_word.views.unit', name=('list_id', 'unit_id')),
    url(r'^word/$', 'gre_word.views.word'),
    url(r'^words/$', 'gre_word.views.words'),
    url(r'^alphabetical/(?P<letter>[a-zA-Z])/$', 'gre_word.views.alphabetical', name='letter'),

    # This url is deprecated, which used to be the url to publish weibo every 10 minutes
    # url(r'^cron/pub_weibo/$', 'gre_word.views.pub_weibo'),

    # Deals with WeChat requests.
    url(r'^weixin/$', 'gre_word.views.weixin'),
)

urlpatterns += staticfiles_urlpatterns()
