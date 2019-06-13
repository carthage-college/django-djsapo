from django.urls import path, re_path

from djsapo.dashboard import views


urlpatterns = [
    re_path(
        '^alert/(?P<pid>\d+)/detail/$', views.detail, name='detail'
    ),
    path(
        'search/', views.search, name='search'
    ),
    path('', views.home, name='home'),
]
