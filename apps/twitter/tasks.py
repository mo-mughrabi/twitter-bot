# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from celery.contrib.methods import task
from celery import task
from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings
from django.db import IntegrityError
from django.db.models import get_model
from celery.utils.log import get_task_logger
from apps.twitter.models import Operation

logger = get_task_logger(__name__)
import tweepy
from tweepy import OAuthHandler
from models import Account


def get_diff(list1,list2):
    """Outputs objects which are in list1 but not list 2"""
    return list(set(list1).difference(set(list2)))


@periodic_task(run_every=crontab(minute="*/1"))
def run_operations():
    """
    """
    logger.info('Run operations is starting up')

    for job in Operation.objects.filter(status='P')[:20]:
        job.run_operation()
        job.status = 'C'
        job.save()

    logger.info('Run operations is ended')
    return u'Success'


@task()
def follow_back(account_id):
        auth = OAuthHandler(getattr(settings, 'TWITTER_CONSUMER_KEY'), getattr(settings, 'TWITTER_CONSUMER_SECRET'))
        account = Account.objects.get(pk=account_id)
        auth.set_access_token(account.access_token, account.secret_key)
        api = tweepy.API(auth)
        #user = api.me()

        follower_ids = []
        for follower in tweepy.Cursor(api.followers).items():
            follower_ids.append(follower.id)

        friend_ids = []
        for friend in tweepy.Cursor(api.friends).items():
            friend_ids.append(friend.id)

        follow_list = get_diff(follower_ids, friend_ids)

        for follower in follow_list:
            Operation.objects.create(user=account, func='follow_user', args='{},'.format(follower))
        return u'Success'

@task()
def unfollow(account_id):
        auth = OAuthHandler(getattr(settings, 'TWITTER_CONSUMER_KEY'), getattr(settings, 'TWITTER_CONSUMER_SECRET'))
        account = Account.objects.get(pk=account_id)
        auth.set_access_token(account.access_token, account.secret_key)
        api = tweepy.API(auth)
        #user = api.me()

        follower_ids = []
        for follower in tweepy.Cursor(api.followers).items():
            follower_ids.append(follower.id)

        friend_ids = []
        for friend in tweepy.Cursor(api.friends).items():
            friend_ids.append(friend.id)

        unfollow_list = get_diff(friend_ids, follower_ids)

        for follower in unfollow_list:
            Operation.objects.create(user=account, func='follow_user', args='{},'.format(follower))
        return u'Success'
