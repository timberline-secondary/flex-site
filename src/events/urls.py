from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.event_list, name='home'),
    url(r'^$', views.event_list, name='list'),
    url(r'^manage/$', views.event_manage, name='manage'),
    url(r'^create/$', views.event_create, name='create'),
    url(r'^(?P<id>\d+)/$', views.event_detail, name='detail'),
    url(r'^(?P<id>\d+)/edit/$', views.event_update, name='update'),
    url(r'^(?P<id>\d+)/copy/$', views.event_copy, name='copy'),
    # url(r'^(?P<id>\d+)/delete/$', views.event_delete, name='delete'),
    url(r'^(?P<pk>\d+)/delete/$', views.EventDelete.as_view(), name='delete'),
    url(r'^(?P<id>\d+)/attendance/$', views.event_attendance, name='attendance'),
    url(r'^(?P<id>\d+)/attendance/keypad/$', views.event_attendance_keypad, name='attendance_keypad_init'),
    url(r'^(?P<id>\d+)/attendance/(?P<block_id>\d+)$', views.event_attendance, name='attendance_by_block'),
    url(r'^staff/$', views.staff_locations, name='staff_locations'),
    url(r'^synervoice/$', views.synervoice, name='synervoice'),

    # Registrations
    url(r'^register/$', views.register, name='register'),
    url(r'^registrations/$', views.registrations_list, name='registrations_list'),
    url(r'^registrations/(?P<id>\d+)/$', views.registrations_delete, name='registrations_delete'),
    url(r'^registrations/all/$', views.registrations_all, name='registrations_all'),
    url(r'^registrations/homeroom/$', views.registrations_homeroom, name='registrations_homeroom'),
    url(r'^registrations/manage/$', views.registrations_manage, name='registrations_manage'),
    # url(r'^registrations/homeroom/$', views.homeroom, name='homeroom'),

]
