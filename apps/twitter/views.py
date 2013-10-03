# -*- coding: utf-8 -*-
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View, TemplateResponseMixin
from pytz import utc


class Home(View):
    """

    """
    template_name = 'twitter/home.html'

    def get(self, request, pk, slug):

        return render(request, self.template_name, c)


