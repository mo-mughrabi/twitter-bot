# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.template import Context
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from social_auth.db.django_models import UserSocialAuth
from social_auth.exceptions import AuthAlreadyAssociated
from exceptions import AuthAccountSuspended
from models import TwitterExtra, User, EmailConfirmation


def social_auth_user(backend, uid, user=None, *args, **kwargs):
    """Return UserSocialAuth account for backend/uid pair or None if it
    doesn't exists.

    Raise AuthAlreadyAssociated if UserSocialAuth entry belongs to another
    user.
    """

    social_user = UserSocialAuth.get_social_auth(backend.name, uid)
    if social_user:
        if user and social_user.user != user:
            msg = _('This %(provider)s account is already in use.')
            raise AuthAlreadyAssociated(backend, msg % {'provider': backend.name})
        elif not user:
            if social_user.user.is_active is False:
                msg = _('Your account is suspended.')
                raise AuthAccountSuspended(backend, msg)
            user = social_user.user

    return {'social_user': social_user,
            'user': user,
            'new_association': False}


def redirect_to_form(*args, **kwargs):
    """ """
    # new user
    if not kwargs['request'].session.get('saved_email') and kwargs.get('user') is None:
        return HttpResponseRedirect(reverse('account-complete-profile'))


def set_username(request, *args, **kwargs):
    """ """
    if kwargs.get('user'):
        username = kwargs['user'].username
    else:
        user = User.objects.all().order_by("-id")[0]
        username = 'auto%s' % str(user.id + 1)
    return {'username': username}


def set_user_details(request, *args, **kwargs):
    """ """
    if kwargs['is_new']:
        user = kwargs['user']
        user.email = request.session.get('saved_email')
        user.full_name = request.session.get('saved_full_name')
        user.save()

        html = get_template('account/email_templates/new_register.html')
        txt = get_template('account/email_templates/new_register.txt')

        c = Context({
            'user': user.username,
            'activation_link': user.get_activation_url(),
            'domain': request.META['HTTP_HOST'],
            'protocol': 'https' if request.is_secure() else 'http',
            'STATIC_URL': getattr(settings, 'STATIC_URL')
        })
        msg = EmailMultiAlternatives(_('Welcome to Twit Robo'), txt.render(c), 'info@twit-robo.mocorner.com',
                                     [user.email, ])
        msg.attach_alternative(html.render(c), "text/html")
        # uncomment below to allow sending outgoing emails
        #msg.send()
        messages.success(request, _('Welcome to Twitbot'))


def social_extra_data(backend, details, response, social_user, uid, user, *args, **kwargs):
    """
    """

    if social_user.provider == 'twitter':
        """ populate extra data for twitter users """
        try:
            tw_user = TwitterExtra.objects.get(user=user)
        except TwitterExtra.DoesNotExist:
            import urlparse
            tokens = urlparse.parse_qs(response.get('access_token'))
            TwitterExtra.objects.create(
                user=user,
                access_token=tokens['oauth_token'][0],
                access_token_secret=tokens['oauth_token_secret'][0],
                screen_name=response.get('screen_name'),
                response=response,
            )


def update_email_validity(backend, details, response, user=None, is_new=False, *args, **kwargs):
    """ """
    if user is None:
        return
    social_user = kwargs['social_user']
    # below functionality, will first check if email is valid and has record in emailconfirmation model
    # if no record found, it will create one
    # then, it would check if the email is invalid and user came through facebook or linkedin
    # if yes, it would mark the email as valid
    confirmation_record, email_is_valid = user.is_email_valid
    if not confirmation_record:
        user.create_email_confirmation(trigger_email=False)

    if social_user.provider in ('facebook', 'linkedin') and details.get('email') and is_new is False and email_is_valid is False:
        if details.get('email') == user.email:
            obj = EmailConfirmation.objects.get(user=user)
            obj.email_is_valid = True
            obj.save()
            obj.user.reload_groups()


def destroy_session_data(backend, details, response, social_user, uid, user, *args, **kwargs):
    """ remove built up data from signing up / signing in - kept in session for step over sign in """
    request = kwargs['request']
    if hasattr(request.session, 'saved_username'):
        del request.session['saved_username']

    if hasattr(request.session, 'saved_full_name'):
        del request.session['saved_full_name']

    if hasattr(request.session, 'saved_email'):
        del request.session['saved_email']

    if hasattr(request.session, 'saved_interests'):
        del request.session['saved_interests']

    if hasattr(request.session, 'saved_join_mailing_list'):
        del request.session['saved_join_mailing_list']