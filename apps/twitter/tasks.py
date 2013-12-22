# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from celery import task
from django.db import IntegrityError
from django.db.models import get_model
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)



@task(name='twitter.say_hello')
def say_hello():
    """
    """
    logger.info('Am saying hello to you')
    return u'Success'
