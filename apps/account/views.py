# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic.base import View, TemplateResponseMixin
from django.contrib.auth import logout as django_logout
from forms import SocialForm, EditProfileForm
from models import EmailConfirmation, User
from django.utils.translation import ugettext_lazy as _, get_language
from django.contrib import messages
from django.views.generic import DeleteView


class Signup(View):
    """  """
    template_name = 'account/signup.html'

    def get(self, request):
        if request.user.is_authenticated():
            return redirect(reverse('home'))
        else:
            return render(request, self.template_name, {})


class Logout(View):
    """

    """

    @method_decorator(login_required)
    def get(self, request):
        django_logout(request)
        return redirect(reverse('home'))


class Verify(View):
    """

    """

    def get(self, request, verification_code):
        try:
            obj = EmailConfirmation.objects.get(email_vc=verification_code, email_is_valid=False)
            obj.email_is_valid = True
            obj.save()
            obj.user.reload_groups()
            messages.success(request, _('Your email has been verified and your account is now active.'))
            if request.user.is_authenticated():
                return redirect(reverse('home'))
            else:
                return redirect(reverse('account-login'))

        except EmailConfirmation.DoesNotExist as e:
            messages.error(request, _('The activation link you are trying to use is invalid.'))
            return redirect(reverse('home'))


class Profile(View):
    """ """
    template_name = 'account/profile.html'

    def get(self, request):
        form = EditProfileForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.info(request,"Your profile has been successfully updated!")
        return render(request, self.template_name, {'form': form})



class DeleteView(DeleteView):
    """

    """
    model = User
    template_name = 'account/confirmation_page.html'

    def get(self, request, pk):
        user = User.objects.get(pk=pk)
        return render(request, self.template_name, {
            'message': 'Are you sure you want to delete user %s' % user.username
        },)

    def post(self, request, pk):
        user = User.objects.get(pk=pk)
        user.delete()
        django_logout(request)
        return redirect(reverse('home'))


class CompleteProfile(View):
    """

    """

    template_name = 'account/complete_profile.html'

    def get(self, request):
        name = getattr(settings, 'SOCIAL_AUTH_PARTIAL_PIPELINE_KEY', 'partial_pipeline')
        full_name = ''
        username = ''
        avatar = ''
        email = ''

        backend = request.session[name]['backend']
        kwargs = request.session[name]['kwargs']
        if backend == 'twitter':
            full_name = kwargs.get('details', '').get('fullname', '')
            username = kwargs.get('details', '').get('username', '')
            avatar = kwargs.get('response', None).get('profile_image_url_https', None)

        initial_context = {'full_name': full_name}
        if username not in ('', u'', None):
            try:
                User.objects.get(username=username)
            except User.DoesNotExist:
                initial_context.update({'username': username})

        if email not in ('', u'', None):
            initial_context.update({'email': email})

        form = SocialForm(initial=initial_context)
        return render(request, self.template_name,
                {'form': form,
                'backend': backend,
                'username': username,
                'avatar': avatar},)

    def post(self, request):
        name = getattr(settings, 'SOCIAL_AUTH_PARTIAL_PIPELINE_KEY', 'partial_pipeline')
        full_name = ''
        avatar = ''
        email = ''

        if name not in request.session:
            raise Http404

        backend = request.session[name]['backend']
        kwargs = request.session[name]['kwargs']
        if backend == 'twitter':
            full_name = kwargs.get('details', '').get('fullname', '')
            username = kwargs.get('details', '').get('username', '')
            avatar = kwargs.get('response', None).get('profile_image_url_https', None)

        initial_context = {}
        if email not in ('', u'', None):
            initial_context.update({'email': email})

        form = SocialForm(request.POST, initial=initial_context)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            request.session['saved_full_name'] = cleaned_data.get('full_name')
            request.session['saved_email'] = cleaned_data.get('email')
            request.session['saved_join_mail_list'] = cleaned_data.get('join_mailing_list')
            return redirect('socialauth_complete', backend=backend)

        return render(request, self.template_name,
                {'form': form,
                'backend': backend,
                'username': username,
                'avatar': avatar},)

