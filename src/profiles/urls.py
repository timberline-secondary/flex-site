from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.PublisherList.as_view(), name='list'),
    url(r'^homeroom/$', views.home_room, name='homeroom'),

]
