from django.urls import path, re_path

from djsapo.dashboard import views


urlpatterns = [
    re_path(
        '^alert/(?P<pid>\d+)/detail/$', views.detail, name='detail'
    ),
    # complete lising
    path(
        'list/', views.list, name='dashboard_list'
    ),
    path(
        'search/', views.search, name='search'
    ),
    path('', views.home, name='home'),
    # export to openxml
    path(
        'openxml/', views.openxml, name='openxml'
    ),
]
