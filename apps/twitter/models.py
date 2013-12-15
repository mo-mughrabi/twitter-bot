# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Account(models.Model):
    """
    """
    tid = models.CharField(_('Twitter ID'), max_length=200)
    screen_name = models.CharField(_('Screen name'), max_length=200)
    access_token = models.CharField(_('Access token'), max_length=200)
    secret_key = models.CharField(_('Secret Key'), max_length=200)
    followers = models.PositiveIntegerField(default=0)
    following = models.PositiveIntegerField(default=0)


class Follower(models.Model):
    """
    """
    account = models.ForeignKey(Account)
    screen_name = models.CharField(_('Screen name'), max_length=200)


class Following(models.Model):
    """
    """
    account = models.ForeignKey(Account)
    screen_name = models.CharField(_('Screen name'), max_length=200)