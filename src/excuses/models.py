from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from flex.utils import default_event_date


class ExcuseReason(models.Model):
    reason = models.CharField(max_length=50)

    def __str__(self):
        return self.reason

    class Meta:
        ordering = ['reason']


class ExcuseQuerySet(models.QuerySet):
    def date(self, date):
        return self.filter(first_date__lte=date, last_date__gte=date)

    def in_block(self, block):
        return self.filter(blocks=block)

    def for_student(self, user):
        return self.filter(students=user)


class ExcuseManager(models.Manager):
    def get_queryset(self):
        return ExcuseQuerySet(self.model, using=self._db)

    def all_on_date(self, date):
        return self.get_queryset().date(date)


class Excuse(models.Model):
    students = models.ManyToManyField(User, limit_choices_to={'is_staff': False})
    reason = models.ForeignKey(ExcuseReason, on_delete=models.SET_NULL, null=True)
    first_date = models.DateField(
        default=default_event_date,
        help_text="This is the first date that the student is excused for the provided reason."
    )
    last_date = models.DateField(
        default=default_event_date,
        help_text="This is the last date that the student is excused for the provided reason."
    )
    blocks = models.ManyToManyField('events.Block', help_text="In which block(s) are the students excused?")

    objects = ExcuseManager()

    def __str__(self):
        return "%s from %s to %s" % (self.reason, self.first_date, self.last_date)

    class Meta:
        ordering = ['-first_date']