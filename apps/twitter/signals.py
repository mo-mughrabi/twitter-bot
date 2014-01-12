# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.account.models import TwitterExtra
from models import Account


@receiver(post_save, sender=TwitterExtra, dispatch_uid='create_twitter_account')
def create_twitter_account(sender, instance=None, created=False, **kwargs):
    if created:
        #resp_json = instance.response
        Account.objects.create(user=instance.user, tid='', screen_name='',
                               access_token=instance.access_token, secret_key=instance.access_token_secret)


