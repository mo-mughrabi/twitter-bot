# -*- coding: utf-8 -*-
import re
from django import forms
from django.core.urlresolvers import reverse
from django.template.defaultfilters import safe
from django.utils.translation import ugettext_lazy as _, get_language
from apps.account.models import User


class SocialForm(forms.Form):
    """

    """
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input-xlarge', 'placeholder': 'Full name...', 'required': ''}))
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'class': 'input-xlarge', 'placeholder': 'Email address...', 'required': ''}))
    join_mailing_list = forms.BooleanField(required=False, widget=forms.CheckboxInput(
                                    attrs={'tabindex': '4', 'class': 'field login-checkbox'}),
                                    label=_('Join a mailing list for your interests'))
    terms = forms.BooleanField(widget=forms.CheckboxInput(attrs={'tabindex': '4', 'class': 'field login-checkbox'}),
                               label=_('I have read and agree with the Terms of Use.'),
                               error_messages={'required': _('Your must agree for the terms and conditions')})

    def __init__(self, *args, **kwargs):
        super(SocialForm, self).__init__(*args, **kwargs)

        if re.match(r'[^@]+@[^@]+\.[^@]+', self.initial.get('email', '')):
            self.fields['email'].widget.attrs['readonly'] = True

        self.fields['email'].error_messages.update({'required': _('Email field is required')})

    def all_fields(self):
        return [field for field in self if not field.is_hidden and field.name not in ('terms', 'join_mailing_list')]

    def clean(self):
        cleaned_data = super(SocialForm, self).clean()

        # validate email unique
        try:
            User.objects.get(email=str(cleaned_data.get('email', None)).lower())
            self._errors['email'] = self.error_class(
                [_(safe('Your email already exists, please use different email address. '))])
            del cleaned_data['email']
        except User.DoesNotExist:
            pass

        return cleaned_data