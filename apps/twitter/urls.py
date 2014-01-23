# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from views import Home, HashtagView

urlpatterns = patterns('',
    url(r'^$', Home.as_view(), name='twitter-home'),
    url(r'^hashtags/$', HashtagView.as_view(), name='twitter-hashtag'),
)