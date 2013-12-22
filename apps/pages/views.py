# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View, TemplateResponseMixin
from apps.twitter.tasks import say_hello


class Home(View):
    """  """
    template_name = 'pages/home.html'

    def get(self, request):
        say_hello.apply_async(countdown=10)
        return render(request, self.template_name, {})


