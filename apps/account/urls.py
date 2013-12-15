# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import patterns, url, include
from views import Signup, Logout, Verify, CompleteProfile, Profile, DeleteView

urlpatterns = patterns('',
    url(r'^sign-up/$', Signup.as_view(), name='account-signup'),
    url(r'^logout/$', Logout.as_view(), name='account-logout'),
    url(r'^profile/$', Profile.as_view(), name='account-profile'),
    url(r'^verify/(?P<verification_code>[-\w]+)/$', Verify.as_view(), name='account-verify'),
    url(r'^complete-profile/$', CompleteProfile.as_view(), name='account-complete-profile'),
    url(r'^delete-user/(?P<pk>[-\w]+)/$', DeleteView.as_view(), name='account-delete-user'),
)

urlpatterns += patterns('',
                        url(r'', include('social_auth.urls'))
)