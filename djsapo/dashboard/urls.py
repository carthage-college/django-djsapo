from django.urls import path, re_path
from django.views.generic import TemplateView

from djsapo.dashboard import views


urlpatterns = [
    re_path('^alert/(?P<aid>\d+)/detail/$', views.detail, name='detail'),
    # complete lising
    path('list/', views.list, name='list'),
    path('search/', views.search, name='search'),
    # Send an email
    path(
        'email/success/',
        TemplateView.as_view(
            template_name='email_form_done.html'
        ),
        name='email_form_done'
    ),
    re_path(
        '^email/(?P<aid>\d+)/(?P<action>[-\w]+)/$',
        views.email_form, name='email_form'
    ),
    # object manager
    path('manager/', views.manager, name='manager'),
    # export to openxml
    path('openxml/', views.openxml, name='openxml'),
    path('', views.home, name='home'),
]
