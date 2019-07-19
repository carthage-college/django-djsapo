from django.urls import include, path, re_path
from django.views.generic import RedirectView, TemplateView
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.contrib import admin

from djauth.views import loggedout
from djsapo.core import views

admin.autodiscover()

handler404 = 'djtools.views.errors.four_oh_four_error'
handler500 = 'djtools.views.errors.server_error'


urlpatterns = [
    # auth
    path(
        'accounts/login/', auth_views.LoginView.as_view(),
        {'template_name': 'registration/login.html'},
        name='auth_login'
    ),
    path(
        'accounts/logout/', auth_views.LogoutView.as_view(),
        {'next_page': reverse_lazy('auth_loggedout')},
        name='auth_logout'
    ),
    path(
        'accounts/loggedout/', loggedout,
        {'template_name': 'registration/logged_out.html'},
        name='auth_loggedout'
    ),
    path(
        'accounts/',
        RedirectView.as_view(url=reverse_lazy('auth_login'))
    ),
    path(
        'denied/',
        TemplateView.as_view(template_name='denied.html'), name='access_denied'
    ),
    # django admin
    path(
        'admin/', admin.site.urls
    ),
    # dashboard
    path(
        'dashboard/', include('djsapo.dashboard.urls')
    ),
    # alert form
    path(
        'success/', TemplateView.as_view(
            template_name='alert/success.html'
        ), name='alert_success'
    ),
    # APIs
    path(
        'kat-matrix/', views.kat_matrix, name='kat_matrix'
    ),
    re_path(
        '^api/(?P<who>[-\w]+)/$', views.people, name='people'
    ),
    # clear cache via ajax post
    re_path(
        '^cache/(?P<ctype>[-\w]+)/clear/', views.clear_cache, name='clear_cache'
    ),
    # home
    path(
        '', views.alert_form, name='alert_form'
    ),
]
urlpatterns += path('admin/', include('loginas.urls')),
