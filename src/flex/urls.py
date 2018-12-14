"""flex URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from events import views as event_views

admin.site.site_header = settings.ADMIN_SITE_HEADER

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', event_views.event_list, name='home'),
    # installed apps
    # url(r'^summernote/', include('django_summernote.urls')),
    # url(r'^accounts/', include('userena.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^select2/', include('django_select2.urls')),
    # custom apps
    url(r'^events/', include(('events.urls', 'events'), namespace='events')),
    url(r'^profiles/', include(('profiles.urls', 'profiles'), namespace='profiles')),
    url(r'^excuses/', include(('excuses.urls', 'excuses'), namespace='excuses')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
