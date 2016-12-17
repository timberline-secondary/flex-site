from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.ProfileList.as_view(), name='list'),
    url(r'^homeroom/$', views.home_room, name='homeroom'),
    url(r'^import/$', views.mass_user_import, name='import'),

]
