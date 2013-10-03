# -*- coding: utf-8 -*-
from social_auth.exceptions import AuthException


class AuthAccountSuspended(AuthException):
    """Account is suspended"""
    pass