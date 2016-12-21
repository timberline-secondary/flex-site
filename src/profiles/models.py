from django.db import models
from django.conf import settings
# from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import ugettext as _
# from userena.models import UserenaBaseProfile


# class UserProfile(UserenaBaseProfile):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL,
#                                 unique=True,
#                                 verbose_name=_('user'),
#                                 related_name='my_profile')
#     favourite_snack = models.CharField(_('favourite snack'),
#                                        max_length=5)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True)
    # first_name = models.CharField(max_length=50, null=True)  // use user.first_name
    # last_name = models.CharField(max_length=50, null=True)
    homeroom_teacher = models.ForeignKey(settings.AUTH_USER_MODEL,
                                         limit_choices_to={'is_staff': True},
                                         related_name='profiles',
                                         null=True, blank=True)
    grade = models.IntegerField(null=True)
    phone = models.CharField(max_length=13, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return str(self.user.username) + " (" + str(self.user.first_name) + " " + str(self.user.last_name) + ")"


def create_profile(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        Profile.objects.create(user=user)

post_save.connect(create_profile, sender=settings.AUTH_USER_MODEL)