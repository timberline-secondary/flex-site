from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.event_list, name='home'),
    url(r'^$', views.event_list, name='list'),
    url(r'^export/$', views.event_list_export, name='export'),
    url(r'^block/(?P<block_id>\d+)/$', views.event_list, name='list_by_block'),
    url(r'^manage/$', views.event_manage, name='manage'),
    url(r'^create/$', views.event_create, name='create'),
    url(r'^(?P<id>\d+)/$', views.event_detail, name='detail'),
    url(r'^(?P<id>\d+)/edit/$', views.event_update, name='update'),
    url(r'^(?P<id>\d+)/copy/$', views.event_copy, name='copy'),
    # url(r'^(?P<id>\d+)/delete/$', views.event_delete, name='delete'),
    url(r'^(?P<pk>\d+)/delete/$', views.EventDelete.as_view(), name='delete'),
    url(r'^(?P<id>\d+)/attendance/$', views.event_attendance, name='attendance'),
    url(r'^(?P<id>\d+)/attendance/keypad/$', views.event_attendance_keypad, name='attendance_keypad_init'),
    url(r'^(?P<id>\d+)/attendance/keypad/disable$', views.event_attendance_keypad_disable, name='attendance_keypad_disable'),
    url(r'^(?P<id>\d+)/attendance/block/(?P<block_id>\d+)/$', views.event_attendance, name='attendance_by_block'),
    url(r'^staff/$', views.staff_locations, name='staff_locations'),
    url(r'^synervoice/$', views.synervoice, name='synervoice'),
    url(r'^stats/$', views.stats2, name='stats'),
    url(r'^stats2/$', views.stats2, name='stats2'),

    # Locations
    url(r'^locations/create/$', views.location_create, name='location_create'),

    # Registrations
    url(r'^register/(?P<id>\d+)/block/(?P<block_id>\d+)/$', views.register, name='register'),
    url(r'^registrations/$', views.registrations_list, name='registrations_list'),
    url(r'^registrations/(?P<id>\d+)/delete$', views.registrations_delete, name='registrations_delete'),
    url(r'^registrations/all/$', views.registrations_all, name='registrations_all'),
    url(r'^registrations/homeroom/$', views.registrations_homeroom, name='registrations_homeroom'),
    url(r'^registrations/manage/$', views.registrations_manage, name='registrations_manage'),
    # url(r'^registrations/homeroom/$', views.homeroom, name='homeroom'),

]
