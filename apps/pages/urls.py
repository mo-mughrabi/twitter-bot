# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import patterns, url, include
from views import Home

urlpatterns = patterns('',
    url(r'^$', Home.as_view(), name='home'),
)