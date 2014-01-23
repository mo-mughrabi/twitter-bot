# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic.base import View, TemplateResponseMixin
from pytz import utc
from forms import HashtagForm
from tasks import follow_back
from tasks import unfollow
from models import Account, Hashtag
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


class Home(View):
    """  """
    template_name = 'twitter/home.html'

    @method_decorator(login_required)
    def get(self, request):

        return render(request, self.template_name, {})

    @method_decorator(login_required)
    def post(self, request):
        account = Account.objects.get(user=request.user)
        if request.POST['form-type'] == u'Follow back':
            follow_back.delay(account.id, )
        else:
            unfollow.delay(account.id, )
        return render(request, self.template_name, {})


class HashtagView(View):
    """
      add delete hash tag
      add pagination if user has many has tags
      """
    template_name = 'twitter/hashtag.html' # < create html file

    @method_decorator(login_required)
    def get(self, request):
        form = HashtagForm()

        hashtag_list = Hashtag.objects.filter(created_user=get_object_or_404(Account, user=request.user))
        paginator = Paginator(hashtag_list, 5)

        page = request.GET.get('page', '1')
        try:
            hashtags = paginator.page(page)
        except PageNotAnInteger:
            hashtags = paginator.page(1)
        except EmptyPage:
            hashtags = paginator.page(paginator.num_pages)

        return render(request, self.template_name,
                      {'hashtags': hashtags,
                       'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = HashtagForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_user = get_object_or_404(Account, user=request.user)
            obj.save()
            messages.success(request, 'Hash tag was saved successfully')
            return redirect(reverse('twitter-hashtag'))

        return render(request, self.template_name, {})


