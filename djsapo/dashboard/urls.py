from django.urls import path, re_path

from djsapo.dashboard import views


urlpatterns = [
    re_path(
        '^alert/(?P<aid>\d+)/detail/$', views.detail, name='detail'
    ),
    # complete lising
    path(
        'list/', views.list, name='list'
    ),
    path(
        'search/', views.search, name='search'
    ),
    # export to openxml
    path(
        'openxml/', views.openxml, name='openxml'
    ),
    path('', views.home, name='home'),
]
