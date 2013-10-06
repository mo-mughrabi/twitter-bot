# -*- coding: utf-8 -*-
import re
from django import forms
from django.core.urlresolvers import reverse
from django.template.defaultfilters import safe
from django.utils.translation import ugettext_lazy as _, get_language
from apps.account.models import User


class EditProfileForm(forms.ModelForm):
    """
    EditProfileForm

    """

    class Meta:
        model = User
        fields = ('full_name', 'gender', 'join_mailing_list', )

        widgets = {
            'full_name': forms.TextInput(attrs={'required': '', 'class': 'input-xxlarge'}),
        }
        field_args = {
            'full_name': {
                'error_messages': {
                    'required': _('Full name is required')
                }
            },
            'username': {
                'error_messages': {
                    'required': _('Username address is required')
                },
                'help_text': ''
            },
        }

    def __init__(self, *args, **kwargs):

        if 'request' in kwargs:
            self.request = kwargs.get('request')
            kwargs.pop('request')

        super(EditProfileForm, self).__init__(*args, **kwargs)

        # required fields to over-ride model
        self.fields['full_name'].required = True

        self.fields['full_name'].widget.attrs.update({'class': 'form-control'})


    def all_fields(self):
        return [field for field in self if not field.is_hidden and field.name not in ('terms', 'captcha')]

    def clean(self):
        cleaned_data = super(EditProfileForm, self).clean()
        return cleaned_data


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

        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['full_name'].widget.attrs.update({'class': 'form-control'})

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