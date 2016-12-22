from datetime import date, datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.core.urlresolvers import reverse

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=120)
    visible_in_event_list = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Location(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return self.room_number
        # str = self.room_number
        # if self.name:
        #     str += " (" + self.name + ")"
        # return str

    class Meta:
        ordering = ['room_number']


class BlockManager(models.Manager):
    def get_flex_1(self):
        return self.get_queryset().get(id=1)

    def get_flex_2(self):
        return self.get_queryset().get(id=2)


class Block(models.Model):
    name = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()

    objects = BlockManager()

    def __str__(self):
        return self.name

    def constant_string(self):
        if self.id == 1:
            return "FLEX1"
        else:
            return "FLEX2"


def default_event_date():
    today = date.today()
    # Wednesday = 2
    wednesday = today + timedelta((2 - today.weekday()) % 7)
    return wednesday


class EventManager(models.Manager):
    def all_for_date(self, event_date, block=None):
        if block:
            qs = block.event_set.all()
        else:
            qs = self.get_queryset()
        return qs.filter(date=event_date)

    def all_for_facilitator(self, user):
        return user.event_set.all()


class Event(models.Model):

    # FLEX_BLOCK_1 = 1
    # FLEX_BLOCK_2 = 2
    # FLEX_BLOCK_CHOICES = (
    #     (FLEX_BLOCK_1, 'Flex-1'),
    #     (FLEX_BLOCK_2, 'Flex-2'),
    # )

    F1_XOR_F2 = 0
    F1_OR_F2 = 1
    F1_AND_F2 = 2
    MULTI_BLOCK_CHOICES = (
        (F1_XOR_F2, 'Can choose one or the other, but not both.'),
        (F1_OR_F2, 'Can choose one block or both blocks.'),
        (F1_AND_F2, 'Both blocks are required.'),
    )

    title = models.CharField(max_length=120)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    date = models.DateField(default=default_event_date)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    blocks = models.ManyToManyField(Block)
    # flex1 = models.BooleanField(default=True)
    # flex2 = models.BooleanField(default=False)
    multi_block_event = models.IntegerField(default=F1_OR_F2, choices=MULTI_BLOCK_CHOICES,
                                            help_text="If the event is running in more than one block, what restrictions"
                                                   " are there for students?"
                                            )
    facilitators = models.ManyToManyField(User, related_name='events',
                                          limit_choices_to={'is_staff': True})
    allow_facilitators_to_modify = models.BooleanField(default=True,
                                                       help_text="If false, only the creator of the event can edit.")
    creator = models.ForeignKey(User)
    updated_timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)
    created_timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    objects = EventManager()

    class Meta:
        ordering = ['-date']

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
                if self.multi_block_event == Event.F1_AND_F2:
                    bl_str += " AND "
                elif self.multi_block_event == Event.F1_OR_F2:
                    bl_str += " OR "
                elif self.multi_block_event == Event.F1_XOR_F2:
                    bl_str += " XOR "
                else:  # shouldn't get here
                    bl_str += " ERROR "
            bl_str += str(block)
            count += 1
        return bl_str

    def block_selection_guide(self):
        blocks = self.blocks.all()
        if len(blocks) > 1:
            return self.multi_block_event
        elif blocks:  # only 1
            return blocks[0].constant_string()

    def flex1(self):
        if Block.objects.get_flex_1() in self.blocks.all():
            return True
        else:
            return False

    def flex2(self):
        if Block.objects.get_flex_2() in self.blocks.all():
            return True
        else:
            return False

    def facilitator_string(self):
        facilitators = self.facilitators.all()
        fac_str = ""
        count = 1
        for fac in facilitators:
            if count > 1:
                fac_str += "<br>"
            fac_str += fac.first_name + "&nbsp;" + fac.last_name
            count += 1
        return fac_str

    def get_editors(self):
        editors = [self.creator]
        if self.allow_facilitators_to_modify:
            for fac in self.facilitators.all():
                if fac not in editors:
                    editors += [fac]
        return editors


class RegistrationManager(models.Manager):
    def create_registration(self, event, student, block):
        # need to check if student already has an event on that date in this block, if so, modify.
        reg = self.create(event=event,
                          student=student,
                          block=block)
        # do something with the book
        return reg

    def get_for_user_block_date(self, student, block, event_date):
        qs = self.get_queryset()
        return qs.filter(student=student).filter(event__date=event_date).filter(block=block)

    def homeroom_registration_check(self, event_date, homeroom_teacher):
        students = User.objects.all().filter(
            is_staff=False,
            profile__homeroom_teacher=homeroom_teacher
        )
        students = students.values('id', 'username', 'first_name', 'last_name')
        students = list(students)

        # get queryset with events? optimization for less hits on db
        qs = self.get_queryset().filter(
            event__date=event_date,
            student__profile__homeroom_teacher=homeroom_teacher
        )
        for student in students:
            user_regs_qs = qs.filter(student_id=student['id'])

            for block in Block.objects.all():
                try:
                    reg = user_regs_qs.get(block=block)
                    student[block.constant_string()] = str(reg.event)
                except ObjectDoesNotExist:
                    student[block.constant_string()] = None

        return students

    def all_attendance(self, event_date):
        students = User.objects.all().filter(
            is_active=True,
            is_staff=False,
        )

        students = students.values('id',
                                   'username',
                                   'first_name',
                                   'last_name',
                                   'profile__grade',
                                   'profile__phone',
                                   'profile__email')
        students = list(students)

        # get queryset with events? optimization for less hits on db
        qs = self.get_queryset().filter(
            event__date=event_date,
        )
        for student in students:
            user_regs_qs = qs.filter(student_id=student['id'])

            for block in Block.objects.all():
                try:
                    reg = user_regs_qs.get(block=block)
                    if reg.absent and not reg.excused:
                        student[block.constant_string()] = block.constant_string()
                except ObjectDoesNotExist:
                    student[block.constant_string()] = block.constant_string() + "-NOREG"

        return students

    def attendance(self, flex_date):
        return self.get_queryset().filter(event__date=flex_date,
                                          student__is_active=True,
                                          student__is_staff=False,
                                          absent=True,
                                          excused=False,
                                          )


class Registration(models.Model):

    # PRESENT = 0
    # ABSENT = 1
    # LATE = 2
    # EXCUSED = 3
    #
    # ATTENDANCE = (
    #     (PRESENT, 'Present'),
    #     (ABSENT, 'Absent'),
    #     (LATE, 'Late'),
    #     (EXCUSED, 'Excused')
    # )

    event = models.ForeignKey(Event)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    updated_timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)
    created_timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    # attendance = models.IntegerField(default=PRESENT, choices=ATTENDANCE)
    absent = models.BooleanField(default=False)
    late = models.BooleanField(default=False)
    excused = models.BooleanField(default=False)

    objects = RegistrationManager()

    class Meta:
        order_with_respect_to = 'event'

    class Meta:
        unique_together = ("event", "student", "block")

    def __str__(self):
        return str(self.student) + ": " + str(self.event)

