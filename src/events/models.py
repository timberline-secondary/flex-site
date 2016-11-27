from django.db import models

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


class Event(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField()
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    block = models.ManyToManyField(Block)
    both_required = models.BooleanField(default=False,
                                        help_text="If the event occurs over multiple blocks, "
                                                  "are students expected to stay for both?")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    updated_timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)
    created_timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.title
