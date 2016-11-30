from datetime import date, datetime, timedelta

from django.contrib.auth.models import User
from django.db import models
from django.core.urlresolvers import reverse

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=120)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Location(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        str = self.room_number
        if self.name:
            str += " (" + self.name + ")"
        return str

    class Meta:
        ordering = ['room_number']


class Block(models.Model):
    name = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.name


def default_event_date():
    today = date.today()
    # Wednesday = 2
    wednesday = today + timedelta((2 - today.weekday()) % 7)
    return wednesday


class Event(models.Model):

    title = models.CharField(max_length=120)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    date = models.DateField(default=default_event_date)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    blocks = models.ManyToManyField(Block)
    both_required = models.BooleanField(default=False,
                                        help_text="If the event occurs over multiple blocks, "
                                                  "are students expected to stay for both?")
    facilitators = models.ManyToManyField(User, related_name='events',
                                          limit_choices_to={'is_staff': True})
    allow_facilitators_to_modify = models.BooleanField(default=True,
                                                       help_text="If false, only the creator of the event can edit.")
    creator = models.ForeignKey(User)
    updated_timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)
    created_timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("events:detail", kwargs={"id": self.id})

    def blocks_str(self):
        blocks = self.blocks.all()
        bl_str = ""
        count = 1
        for block in blocks:
            if count > 1:
                if self.both_required:
                    bl_str += " and "
                else:
                    bl_str += " or "
            bl_str += str(block)
            count += 1
        return bl_str

