from django.contrib import messages
from django.contrib.auth import user_logged_in
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

from django.db.models.signals import post_save
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from events.models import default_event_date


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


class ExcuseReasons(models.Model):
    reason = models.CharField(max_length=50)

    def __str__(self):
        return self.reason

    class Meta:
        ordering = ['reason']


class ExcuseManager(models.Manager):
    def excused_on_day(self, date):
        qs = self.get_querset().filter(first_date__lte=date, last_date__gte=date)
        qs = qs.select_related('student', 'reason')
        return qs


class Excuse(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': False})
    reason = models.ForeignKey(ExcuseReasons, on_delete=models.SET_NULL, null=True)
    first_date = models.DateField(
        default=default_event_date,
        help_text="This is the first date that the student is excused for the given reason."
    )
    last_date = models.DateField(
        default=default_event_date,
        help_text="This is the last date that the student is excuses for the given reason."
    )

    objects = ExcuseManager()

    class Meta:
        ordering = ['-first_date']


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    homeroom_teacher = models.ForeignKey(settings.AUTH_USER_MODEL,
                                         limit_choices_to={'is_staff': True},
                                         related_name='profiles',
                                         null=True, blank=True)
    grade = models.IntegerField(null=True, blank=True)
    phone = models.CharField(max_length=13, null=True, blank=True, help_text="Format: (000)000-0000")
    email = models.EmailField(null=True, blank=True)
    excused = models.BooleanField(default=False, help_text="Student is excused from registering for Flex.")
    excused_reason = models.CharField(null=True, blank=True, max_length=25, help_text='This reason will show in place '
                                                                                      'of an event name on the lists')
    password_change_required = models.BooleanField(default=True)

    def __str__(self):
        return str(self.user.username) + " (" + str(self.user.first_name) + " " + str(self.user.last_name) + ")"


def create_profile(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        Profile.objects.create(user=user)


post_save.connect(create_profile, sender=User)
