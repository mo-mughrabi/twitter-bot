# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from binascii import hexlify
from django.db.models.signals import post_syncdb
import os
import random
import re
import datetime
import string
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractBaseUser, Group
from django.core import validators
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import force_bytes
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    """
        UserManager()
    """

    def create_user(self, username, email=None, password=None, first_name=None, last_name=None, **extra_fields):
        """ create user using simple form / with password + extra fields (gender, birthday) """
        if not username:
            raise ValueError('Users must have a username')

        full_name = '%s%s%s' % (
            first_name if first_name is not None else '',
            '' if (first_name is None or last_name is None) else ' ',
            last_name if last_name is not None else ''
        )

        user = self.model(
            username=username,
            email=UserManager.normalize_email(email),
            full_name=full_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, date_of_birth, full_name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            username=username,
            full_name=full_name,
            email=UserManager.normalize_email(email),
            password=password,
            date_of_birth=date_of_birth,
            is_staff=True
        )
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def all_active(self):
        return self.get_query_set().filter(is_active=True)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Accounts/User
    """
    GENDERS = (
        (u'M', _('Male')),
        (u'F', _('Female')),
    )
    username = models.CharField(_('username'), max_length=30, unique=True,
                                help_text=_('Letters, numbers and '
                                            '@/./+/-/_ characters, you can update your '
                                            'username once every day maximum.'),
                                validators=[
                                    validators.RegexValidator(re.compile('^[\w.@+-]+$'), _('Enter a valid username.'),
                                                              'invalid')
                                ])

    # email / email verification code / email verification code expiry / email is valid?
    email = models.EmailField(_('email address'), unique=True, blank=False, null=False)

    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    join_mailing_list = models.BooleanField(default=False,
                                            help_text=_('Tick if you wish to receive updates about Twit Robo'))
    failed_login_attempt = models.IntegerField(_('failed login attempt'), default=0)

    # user details and information
    full_name = models.CharField(_('full name'), max_length=30, )
    date_of_birth = models.DateField(_('birthday'), null=True, blank=True)

    gender = models.CharField(_('gender'), max_length=1, blank=True, null=True, choices=GENDERS)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'date_of_birth', 'full_name', ]

    def __unicode__(self):
        return u'%s' % self.username

    def __str__(self):
        # Note use of django.utils.encoding.force_bytes() here because
        # first_name and last_name will be unicode strings.
        return force_bytes('%s' % self.username)

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

    @property
    def first_name(self):
        try:
            return self.full_name.split(' ')[0]
        except IndexError:
            return self.full_name

    @property
    def last_name(self):
        try:
            return self.full_name.split(' ')[1]
        except IndexError:
            return self.full_name

    @property
    def display_name(self):
        return u'%s' % self.full_name

    @property
    def email_validity(self):
        return self.is_email_valid[0]

    @property
    def is_email_valid(self):
        """ """
        try:
            obj = EmailConfirmation.objects.get(user=self)
            return True, obj.email_is_valid
        except EmailConfirmation.DoesNotExist:
            return False, False

    def mark_email_valid(self):
        try:
            obj = EmailConfirmation.objects.get(user=self)
            obj.email_is_valid = True
            obj.save()
        except EmailConfirmation.DoesNotExist:
            return False

    def get_absolute_url(self):
        return reverse('account-profile', args=[self.username, ])

    def get_activation_url(self):
        # returns activation url
        return reverse('account-verify', args=[self.emailconfirmation.email_vc, ])

    def create_email_confirmation(self, trigger_email=True):
        """ function will be used to create
            email confirmation and track them"""
        EmailConfirmation.objects.create(user=self,
                                         email_vc=hexlify(os.urandom(5)),
                                         email_vc_expiry=datetime.datetime.utcnow().replace(tzinfo=utc) +
                                                         datetime.timedelta(hours=3))

    def reload_groups(self):
        confirmation_record, email_is_valid = self.is_email_valid
        registered_users = Group.objects.get(name='registered users')
        unverified_users = Group.objects.get(name='unverified users')
        groups = self.groups.all().values_list('id')
        if groups:
            self.groups.remove(*groups[0])
        if email_is_valid:
            self.groups.add(registered_users)
        else:
            self.groups.add(unverified_users)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        is_new = False
        self.username = self.username.lower()
        self.email = self.email.lower()
        if not self.pk:
            is_new = True

        super(User, self).save(force_insert=False, force_update=False, using=None, update_fields=None)

        if is_new:
            self.create_email_confirmation()
            self.reload_groups()


class EmailConfirmation(models.Model):
    """
     details of email confirmation
    """
    user = models.OneToOneField(getattr(settings, 'AUTH_USER_MODEL'), unique=True)
    email_vc = models.CharField(_('Email verification code'), max_length=100, default='')
    email_vc_expiry = models.DateTimeField(_('Email verification code expiry'), null=True, blank=True)
    email_is_valid = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s' % self.user.username

    def __str__(self):
        # Note use of django.utils.encoding.force_bytes() here because
        # first_name and last_name will be unicode strings.
        return force_bytes('%s' % self.user.username)

    def get_absolute_url(self):
        # returns activation url
        return reverse('accounts-verify', args=[self.email_vc, ])


class PasswordRecoveryManager(models.Manager):
    def set_random_password(self, password_recovery):
        try:
            random_password = ''.join(
                random.choice(string.letters) for i in xrange(getattr(settings, 'SF_PASS_PHRASE_LENGTH', 15)))
            user = User.objects.get(pk=password_recovery.user.id)
            user.set_password(random_password)
            user.save()
            return random_password
        except:
            return False

    def is_valid(self, pass_phrase):
        try:
            obj = self.get_query_set().get(pass_phrase=pass_phrase, pass_usage='N',
                                           expires_at__gte=datetime.datetime.now())
            obj.pass_usage = 'U'
            obj.save()
            return obj
        except self.model.DoesNotExist:
            return False

    def create_pass_phrase(self, email, requestor_ip):

        random_pass_phrase = ''.join(
            random.choice(string.letters) for i in xrange(getattr(settings, 'PASS_PHRASE_LENGTH', 15)))

        try:
            # first make sure random string is unique to the user
            # if exists then recursively call the same function
            # until a random pass phrase is found

            self.get(pass_phrase=random_pass_phrase,
                     user=User.objects.get(email=email))
            self.create_pass_phrase(email, requestor_ip)

        except self.model.DoesNotExist:

            rec = self.create(
                user=User.objects.get(email=email),
                requestor_ip=requestor_ip,
                expires_at=datetime.datetime.now() + datetime.timedelta(
                    hours=getattr(settings, 'PASS_PHRASE_EXPIRY', 2)),
                pass_phrase=random_pass_phrase,
            )
            rec.save()
            return rec
        except Exception as e:
            raise e


class PasswordRecovery(models.Model):
    STATUS_USED = 'U'
    STATUS_NEW = 'N'
    _PASS_USAGES = (
        (STATUS_USED, _('Used')),
        (STATUS_NEW, _('New'))
    )
    _PASS_USAGES_DEFAULT = 'N'

    user = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL'), db_index=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    requestor_ip = models.IPAddressField()
    pass_phrase = models.CharField(max_length=100)
    pass_usage = models.CharField(
        max_length=2, choices=_PASS_USAGES, default=_PASS_USAGES_DEFAULT)

    objects = PasswordRecoveryManager()

    class Meta:
        db_table = 'accounts_password_recovery'

    def __unicode__(self):
        return u'%s' % self.user.username

    def __str__(self):
        # Note use of django.utils.encoding.force_bytes() here because
        # first_name and last_name will be unicode strings.
        return force_bytes('%s' % self.user.username)


class TwitterExtraManager(models.Manager):
    """
    """


class TwitterExtra(models.Model):
    """
    accounts / twitter
    """

    user = models.OneToOneField(getattr(settings, 'AUTH_USER_MODEL'))
    access_token = models.CharField(max_length=100, )
    access_token_secret = models.CharField(max_length=100, )
    screen_name = models.CharField(max_length=100, unique=True, )
    link = models.URLField(null=True, blank=True, )
    avatar = models.ImageField(null=True, blank=True, upload_to='accounts/avatar/twitter/')
    response = models.TextField(null=True, blank=True)

    objects = TwitterExtraManager()

    def __unicode__(self):
        return u'TwitterExtra - %s' % self.user.username

    def __str__(self):
        # Note use of django.utils.encoding.force_bytes() here because
        # first_name and last_name will be unicode strings.
        return force_bytes('TwitterExtra - %s' % self.user.username)