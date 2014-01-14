# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View, TemplateResponseMixin
from pytz import utc
from tasks import follow_back
from tasks import unfollow
from models import Account


class Home(View):
    """  """
    template_name = 'twitter/home.html'

    def get(self, request):

        return render(request, self.template_name, {})

    def post(self, request):
        account = Account.objects.get(user=request.user)
        if request.POST['form-type'] == u'Follow back':
            follow_back.delay(account.id,)
        else:
            unfollow.delay(account.id,)
        return render(request, self.template_name, {})