from django.conf.urls import url

from . import views

app_name = "profiles"

urlpatterns = [
    # url(r'^$', views.ProfileList.as_view(), name='list'),
    # url(r'^import/$', views.mass_user_import, name='import'),
    url(r'^update/mass/$', views.mass_update, name='mass_update'),
    url(r'^(?P<id>\d+)/reset/$', views.reset_password_to_default, name='reset_password'),
    url(r'^permissions/update/$', views.permissions_update, name='permissions_update'),

]
