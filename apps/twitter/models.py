# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from tweepy import OAuthHandler
import tweepy


class Account(models.Model):
    """
    """
    user = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL'))
    tid = models.CharField(_('Twitter ID'), max_length=200)
    screen_name = models.CharField(_('Screen name'), max_length=200)
    access_token = models.CharField(_('Access token'), max_length=200)
    secret_key = models.CharField(_('Secret Key'), max_length=200)
    followers_sum = models.PositiveIntegerField(default=0)
    following_sum = models.PositiveIntegerField(default=0)


class Follower(models.Model):
    """
    """
    account = models.ForeignKey(Account, related_name='followers')
    screen_name = models.CharField(_('Screen name'), max_length=200)


class Following(models.Model):
    """
    """
    account = models.ForeignKey(Account, related_name='following')
    screen_name = models.CharField(_('Screen name'), max_length=200)


class Hashtag(models.Model):
    """ you will write a model to hold
    1. name hash tag key - slug
    2. last time of sync - timedate
    3. user who created the hashtag - foreign key with user
    4. number of times it retweeted/favirate - integer
    4. operation (retweet or favirate) - char field with choice

    ./manage.py sql twitter
    ./manage.py schemamigration twitter --auto
    ./manage.py migrate twitter
    """

    #models.SlugField() # this won't allow special characters #(**#$*
    FUNCTIONS = (
        ('R', 'Retweet'),
        ('F', 'Favourites'),
    )

    hash_tag_key = models.SlugField()
    last_time_sync = models.DateTimeField(auto_now_add=True)
    created_user = models.ForeignKey(Account, related_name='created_user')
    number_retweet_or_favourite = models.IntegerField(default=0)
    retweet_or_favourite = models.CharField(_('Retweet or favourites'), max_length=10,
                                            choices=FUNCTIONS, default='R')


class Operation(models.Model):
    """
    """
    STATUSES = (
        ('P', 'Pending'),
        ('C', 'Completed')
    )
    FUNCTIONS = (
        ('follow_user', 'Follow user'),
        ('unfollow_user', 'Unfollow user'),
        ('retweet', 'Retweet'),
        ('favourite', 'Favourite'),
    )
    perform_at = models.DateTimeField(auto_now_add=True)
    performed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=2, choices=STATUSES, default='P')
    user = models.ForeignKey(Account)
    func = models.CharField(max_length=200, choices=FUNCTIONS)
    args = models.CharField(max_length=100)
    kwargs = models.CharField(max_length=200, null=True, blank=True)

    def run_operation(self):
        # execute operation based on type and args
        auth = OAuthHandler(getattr(settings, 'TWITTER_CONSUMER_KEY'), getattr(settings, 'TWITTER_CONSUMER_SECRET'))
        auth.set_access_token(self.user.access_token, self.user.secret_key)
        api = tweepy.API(auth)
        #user = api.me()
        try:
            args = self.args.split(',')
        except :
            # handle if args is a single argument or none
            raise
        if self.func == 'follow_user':
            api.create_friendship(args[0])
        if self.func == 'unfollow_user':
            api.destroy_friendship(args[0])
        if self.func == 'retweet':
            api.retweet(args[0])
        if self.func == 'favourite':
            api.create_favorite(args[0])

