from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

from django.db.models.signals import post_save
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from excuses.models import Excuse


class PasswordResetRequiredMiddleware(object):

    def process_request(self, request):
        result = None
        try:
            if not request.user.is_authenticated:
                result = None
            elif request.path == reverse('auth_password_change_done'):
                request.user.profile.password_change_required = False
                request.user.profile.save()
                messages.success(request, "Password successfully changed.")
                result = redirect('home')
            elif request.user.profile.password_change_required:
                if request.path != reverse('auth_password_change') and \
                   request.path != reverse('auth_logout'):
                    result = HttpResponseRedirect(reverse('auth_password_change'))
            else:
                result = None
        except Profile.DoesNotExist:
            messages.error(request, "You don't seem to have a profile?")

        return result


class ProfileManager(models.Manager):
    def all_active_students(self):
        qs = self.get_queryset().select_related('user')
        return qs.filter(user__is_active=True, user__is_staff=False)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    homeroom_teacher = models.ForeignKey(settings.AUTH_USER_MODEL,
                                         on_delete=models.SET_NULL,
                                         limit_choices_to={'is_staff': True},
                                         related_name='students',
                                         null=True, blank=True
                                         )
    grade = models.IntegerField(null=True, blank=True)
    phone = models.CharField(max_length=13, null=True, blank=True, help_text="Format: (000)000-0000")
    email = models.EmailField(null=True, blank=True)
    permission = models.NullBooleanField(null=True)
    password_change_required = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now=True)  # Used to determine if student is still active after an import.

    objects = ProfileManager()

    def __str__(self):
        return str(self.user.username) + " (" + str(self.user.first_name) + " " + str(self.user.last_name) + ")"


def create_profile(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        Profile.objects.create(user=user)


post_save.connect(create_profile, sender=User)
