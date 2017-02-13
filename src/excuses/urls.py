from django.conf.urls import url

from excuses import views

urlpatterns = [
    url(r'^all/$', views.excuse_list, name='excuse_list'),
    url(r'^create/$', views.excuse_create, name='excuse_create'),
    url(r'^(?P<id>\d+)/edit/$', views.excuse_edit, name='excuse_edit'),
    url(r'^(?P<pk>\d+)/delete/$', views.ExcuseDelete.as_view(), name='excuse_delete'),

]