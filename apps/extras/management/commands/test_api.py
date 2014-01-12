# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.core import management
import os
from django.conf import settings
import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from apps.twitter.models import Account, Operation


def get_diff(list1,list2):
    """Outputs objects which are in list1 but not list 2"""
    return list(set(list1).difference(set(list2)))

class Command(BaseCommand):
    args = '<No arguments>'

    def handle(self, *args, **options):
        auth = OAuthHandler(getattr(settings, 'TWITTER_CONSUMER_KEY'), getattr(settings, 'TWITTER_CONSUMER_SECRET'))
        account = Account.objects.get(pk=2)
        auth.set_access_token(account.access_token, account.secret_key)
        api = tweepy.API(auth)
        user = api.me()

        follower_ids = []
        for follower in tweepy.Cursor(api.followers).items():
            follower_ids.append(follower.id)

        friend_ids = []
        for friend in tweepy.Cursor(api.friends).items():
            friend_ids.append(friend.id)

        follow_list = get_diff(follower_ids, friend_ids)

        for follower in follow_list:
            Operation.objects.create(user=account, func='follow_user', args='{},'.format(follower))
