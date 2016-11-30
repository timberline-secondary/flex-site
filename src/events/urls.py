from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.event_list, name='home'),
    url(r'^$', views.event_list, name='list'),
    url(r'^create/$', views.event_create, name='create'),
    url(r'^(?P<id>\d+)/$', views.event_detail, name='detail'),
    url(r'^(?P<id>\d+)/edit/$', views.event_update, name='update'),
    url(r'^(?P<id>\d+)/delete/$', views.event_delete, name='delete'),
]
