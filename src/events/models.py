import mimetypes
import urllib
from datetime import date, timedelta, datetime
from enum import Enum

import embed_video
import os

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db import OperationalError, models
from django.urls import reverse
from django.db.models.signals import post_save
from django.utils import timezone

from embed_video.backends import detect_backend, UnknownBackendException

# Create your models here.
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFill, SmartResize, ResizeToFit

from excuses.models import Excuse
from flex.utils import default_event_date


class CoreCompetency(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField()
    link = models.URLField()
    icon = models.ImageField(null=True, blank=True, upload_to="icons/")

    class Meta:
        verbose_name_plural = "Core Competencies"

    def __str__(self):
        return self.name


class Category(models.Model):
    COLOR_CHOICES = (  # From bootstrap classes/highlighting
        (None, 'None'),
        ('warning', 'Yellow'),
        ('success', 'Green'),
        ('info', 'Blue'),
        ('danger', 'Red'),
    )
    DEFAULT_CATEGORY_ID = 1
    name = models.CharField(max_length=120)
    abbreviation = models.CharField(max_length=4)
    visible_in_event_list = models.BooleanField(default=False)
    sort_priority = models.IntegerField(default=0)
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, default=None, blank=True, null=True,
                             help_text="Events will be highlighted with this color in the events list",)
    description = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['-sort_priority']

    def __str__(self):
        return self.name

    @classmethod
    def get_default(cls):
        try:
            if cls.objects.filter(name="Support").exists():
                return cls.objects.get(name="Support")
            else:
                return cls.objects.all().first()
        except OperationalError:
            pass  # tables don't exist, could happen when creating a new environment
            


class Location(models.Model):
    room_number = models.CharField(max_length=20, unique=True, help_text="e.g. B201")
    name = models.CharField(max_length=120, null=True, blank=True, help_text="e.g. Hackerspace (or) Couture's Room")

    def __str__(self):
        return self.room_number

    def get_name(self):
        if self.name:
            return self.name
        else:
            return ""

    def get_detailed_name(self):
        name_str = self.room_number
        if self.name:
            name_str += " (" + self.name + ")"
        return name_str

    def get_name_with_conflicts(self, date):
        events = self.event_set.filter(date=date)
        return self.get_detailed_name() + "" + str(events)

    class Meta:
        ordering = ['room_number']


class BlockManager(models.Manager):

    def get_flex_1(self):
        return self.active()[0]

    def get_flex_2(self):
        if not self.single_block():
            return self.active()[1]
        else:
            return None

    def single_block(self):
        """Check if the site is set up with only a single block, returns True or False
        """
        return self.active().count() == 1

    def get_only(self):
        return self.active().first()


    def active(self):
        return self.get_queryset().filter(active=True)

    def get_by_num(self, block_num):
        """ Gets the 1st or second active block """
        if int(block_num) == 1:
            return self.get_flex_1()
        elif not self.single_block() and int(block_num) == 2:
            return self.get_flex_2()
        else:
            return ValueError ("block_num was not 1 or 2.  Only two active blocks are currently supported")

    def get_num_from_id(self, id):
        """ Given a block object's ID, return 1 or 2 if it is the
        1st or second active block """
        if id == self.get_flex_1().id:
            return 1
        elif not self.single_block() and id == self.get_flex_2().id:
            return 2
        else:
            return ValueError ("That block is not active.")


class Block(models.Model):
    name = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()
    active = models.BooleanField(default=True)

    objects = BlockManager()

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return self.name

    def constant_string(self):
        """ Return either  FLEX1 or FLEX2 based on whether this is the first or second active flex block
        as there should only be one or two"""
        if self == Block.objects.get_flex_1():
            return "FLEX1"
        else:
            return "FLEX2"

    def synervoice_absent_string(self):
        return "F" + str(self.id) + "-ABS"

    def synervoice_noreg_string(self):
        return "F" + str(self.id) + "-NOREG"

    def synervoice_noreg_string(self):
        return "F" + str(self.id) + "-PRESENT_OR_EXCUSED"


class EventManager(models.Manager):
    def all_for_date(self, event_date, block=None):
        if block:
            qs = block.event_set.all()
        else:
            qs = self.get_queryset()
        return qs.filter(date=event_date)

    def all_visible_on_date(self, date):
        return self.get_queryset().filter(date=date, category__visible_in_event_list=True)

    def all_for_facilitator(self, user):
        return user.event_set.all()

    def all_active(self):
        """ Only events with at least one active block """
        return self.get_queryset().filter(blocks__in=Block.objects.active())


class Event(models.Model):

    F1_XOR_F2 = 0
    F1_OR_F2 = 1
    F1_AND_F2 = 2
    MULTI_BLOCK_CHOICES = (
        (F1_XOR_F2, 'Can choose one or the other, but not both.'),
        (F1_OR_F2, 'Can choose one block or both blocks.'),
        (F1_AND_F2, 'Both blocks are required.'),
    )

    title = models.CharField(max_length=120)
    description = models.TextField(null=True, blank=True)  # MCE widget validation fails if required
    # description_image_file = models.ImageField(upload_to='images/', null=True, blank=True)
    description_image_file = ProcessedImageField(upload_to='images/', null=True, blank=True,
                                                 processors=[ResizeToFit(400, 400, upscale=False)],
                                                 format='JPEG',
                                                 options={'quality': 80},
                                                 help_text="Upload an image directly from your computer.  You can also "
                                                           "get an image from the web by pasting a direct link to the "
                                                           "image in the Description link field below.",
                                                 verbose_name="Image",
                                                 )
    description_link = models.URLField(
        "Description link (image, video, file, or webpage)",
        null=True, blank=True,
        help_text="An optional link to provide with the text description. Links to videos (YouTube or Vimeo) "
                  "or an image (must end in .png, .jpg, or .gif) will be embedded within the description."
                  "If the link is to another web page or a file, it will just display the link.")

    category = models.ForeignKey(Category, default=Category.DEFAULT_CATEGORY_ID, on_delete=models.SET_NULL, null=True,
                                 help_text="By default, events are sorted by category in the events list.")
    competencies = models.ManyToManyField(CoreCompetency, blank=True,
                                          help_text="The Core Competencies relevant to this event.")
    date = models.DateField(default=default_event_date)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    blocks = models.ManyToManyField(Block, help_text="In which block(s) will this event occur?")
    multi_block_event = models.IntegerField(
        default=F1_OR_F2,
        choices=MULTI_BLOCK_CHOICES,
        help_text="If the event is running in more than one block, what restrictions are there for students?  "
                  "This field is ignored if the event only occurs during one block.")
    facilitators = models.ManyToManyField(User, related_name='events',
                                          limit_choices_to={'is_staff': True})
    allow_facilitators_to_modify = models.BooleanField(
        default=True,
        help_text="If false, only the creator of the event can edit.  If true, then any staff member that is listed as "
                  "a facilitator will be able to edit the event.  The creator will always be able to edit this event, "
                  "even if they are not listed as one of the facilitators.")
    registration_cut_off = models.DurationField(
        default=timedelta(days=0, hours=0, minutes=5, seconds=0),
        help_text="How long before the start of the event does registration close?  After this time, "
                  "students will no longer be able to register for the event, nor will they be able to delete it "
                  "if they've already registered.")
    allow_registration_after_event_has_started = models.BooleanField(
        default=False,
        help_text="Students can continue to register for this event after it has already started, for the amount of "
                  "time indicated in the 'Registration cut off time'.  For example, if your cut off time is set to "
                  "5 minutes and this option is selected, then students will still be able to register for your event "
                  "until 5 minutes AFTER your event has started (rather than being cut off 5 minutes BEFORE your "
                  "event starts)."
    )
    max_capacity = models.PositiveIntegerField(
        default=30,
        help_text="The maximum number of students that can register for this event.  Once the maximum is reached, "
                  "students will no longer be able to register for this event.")

    # generally non-editable fields

    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)
    created_timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    is_keypad_initialized = models.BooleanField(
        default=False,
        help_text="If keypad entry is required, leave this field false and turn it on through the event's attendance "
                  "page so that the proper scripts will run.")
    objects = EventManager()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("events:detail", kwargs={"id": self.id})

    def is_single_block(self):
        return self.blocks.filter(active=True).count() == 1

    def cache_remote_image(self):
        """
        Check if an image link was provided, if so, overwrite current description_image_file:
        Take an image from the description field, download it to a temp file, and save it to the database in
        description_image_file.
        """
        external_image_url = self.get_external_image_link()
        if external_image_url:
            img_temp = NamedTemporaryFile(delete=True)
            # http://stackoverflow.com/questions/24226781/changing-user-agent-in-python-3-for-urrlib-request-urlopen
            try:
                request = urllib.request.Request(
                    external_image_url,
                    data=None,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
                    }
                )
                img_temp.write(urllib.request.urlopen(request).read())
            except urllib.error.HTTPError:
                return False
            except Exception as e:
                # don't worry about errors in this process for now, just ignore broken links etc.
                return False

            img_temp.flush()
            self.description_image_file.save(os.path.basename(external_image_url), File(img_temp))
            self.description_link = None  # After image is cached, remove link.
            self.save()

        return True

    def copy(self, num, user=None):
        """
        Create a copy of this event, one week later, recursively num times.
        """
        dates = []
        date = self.date
        if num > 0:
            for i in range(num):
                date += timedelta(7)
                dates.append(date)

                # M2M relations
                facilitators = self.facilitators.all()
                blocks = self.blocks.filter(active=True)
                competencies = self.competencies.all()

                duplicate_event = self
                # https://docs.djangoproject.com/en/1.10/topics/db/queries/#copying-model-instances
                duplicate_event.pk = None  # autogen a new primary key (will create a new record)
                duplicate_event.date = date
                
                if user is not None:
                    duplicate_event.creator = user

                duplicate_event.save()
                duplicate_event.blocks.set(blocks)
                duplicate_event.facilitators.set(facilitators)
                duplicate_event.competencies.set(competencies)

        return dates

    def get_video_embed_link(self, backend):
        if type(backend) is embed_video.backends.YoutubeBackend:
            return "https://www.youtube.com/embed/" + backend.get_code() + "?rel=0"
        elif type(backend) is embed_video.backends.VimeoBackend:
            return "https://player.vimeo.com/video/" + backend.get_code()
        else:
            return None

    # def get_image_url(self): #assumes its an image already.
    #     if self.description_image_file:
    #         return self.description_image_file.url
    #     else:
    #         return self.description_link

    def video(self):
        if not self.description_link:
            return None
        try:
            backend = detect_backend(self.description_link)

            return self.get_video_embed_link(backend)
        except UnknownBackendException:
            return None

    def get_external_image_link(self):
        """ Returns the description link if it is an image, otherwise returns None"""
        if not self.description_link:
            return None
        # http://stackoverflow.com/questions/10543940/check-if-a-url-to-an-image-is-up-and-exists-in-python
        mimetype, encoding = mimetypes.guess_type(self.description_link)
        if mimetype and mimetype.startswith('image'):
            return self.description_link
        else:
            return None

    def both_required(self):
        blocks = self.blocks.filter(active=True)
        if blocks.count() > 1 and self.multi_block_event == self.F1_AND_F2:
            return True
        else:
            return False

    def blocks_str(self):
        blocks = self.blocks.filter(active=True)
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

    def blocks_str_explanation(self):
        if self.blocks.filter(active=True).count() > 1:
            return dict(Event.MULTI_BLOCK_CHOICES).get(self.multi_block_event)
        else:
            return None

    def block_selection_guide(self):
        blocks = self.blocks.filter(active=True)
        if len(blocks) > 1:
            return self.multi_block_event
        elif blocks:  # only 1
            return blocks[0].constant_string()

    def flex1(self):
        if Block.objects.get_flex_1() in self.blocks.filter(active=True):
            return True
        else:
            return False

    def flex2(self):
        if Block.objects.get_flex_2() in self.blocks.filter(active=True):
            return True
        else:
            return False

    def facilitator_string(self):
        facilitators = self.facilitators.all()
        fac_str = ""
        count = 1
        for fac in facilitators:
            if count > 1:
                fac_str += ", "
            fac_str += fac.first_name + " " + fac.last_name
            count += 1
        return fac_str

    def get_editors(self):
        editors = [self.creator]
        if self.allow_facilitators_to_modify:
            for fac in self.facilitators.all():
                if fac not in editors:
                    editors += [fac]
        return editors

    # def is_available_by_block(self, user):
    #     """
    #     Check when this event is available for the user
    #     :param user:
    #     :return: A dictionary of tuples, with a key for each block, e.g:
    #     return {"Flex-1": (is_available, already_registered, reason_not_available),
    #             "Flex-2": (is_available, already_registered, reason_not_available)
    #             }
    #     """
    #     d = {}  # dictionary of data
    #     available = False # if available in at least one block
    #     for block in Block.objects.active():
    #         d[block] = {}
    #         d[block]["available"], d[block]["already"], d[block]["explanation"] = self.is_available(user, block)
    #         if d[block]["available"]:
    #             available = True
    #
    #     return d, available

    def is_available(self, user, block):
        """
        Check if this event is available in this block or if it conflicts
         with a user's current registrations, attendance max, and cutoff times
        :param user:
        :param block:
        :return: A tuple (boolean, boolean, string) -> (is_available, already_registered, reason_not_available)
        """
        is_avail = True
        already_reg = False
        reason = None

        if self.is_full(block):
            is_avail = False
            reason = "This event is full."
        elif self.is_registration_closed(block):
            is_avail = False
            reason = "The deadline to register for this event has passed."
        else:  # check if the user is already registered for for something in the block
            regs = user.registration_set.filter(event__date=self.date)
            regs_count = regs.count()
            #print(regs_count)
            for reg in regs:
                already_reg, reason = reg.is_conflict(self, block, regs_count)
                if reason is not None:
                    is_avail = False
                    break  # no need to check other block if we already have a conflict.

        return is_avail, already_reg, reason

    def is_registration_closed(self, block):
        if block is None:
            block = Block.objects.get_flex_1()

        event_start = timezone.make_aware(datetime.combine(self.date, block.start_time))
        if self.allow_registration_after_event_has_started:
            cut_off = event_start + self.registration_cut_off
        else:
            cut_off = event_start - self.registration_cut_off

        now = timezone.localtime(timezone.now())
        return now > cut_off

    def is_full(self, block=None):
        """
        :param block:
        :return: If block is None return True if all blocks are full.
        """
        if block:
            is_full = self.get_attendances(block) >= self.max_capacity
        else:
            is_full_by_block = []
            for att in self.get_attendances(block):
                is_full_by_block.append(att >= self.max_capacity)

            is_full = all(is_full_by_block)
        return is_full

    def get_attendances(self, block=None):
        if block:
            result = self.registration_set.filter(block=block).count()
        else:
            result = []
            for block in self.blocks.filter(active=True):
                result.append(self.registration_set.filter(block=block).count())
        return result


def event_post_save(sender, instance, **kwargs):
    post_save.disconnect(event_post_save, sender=sender)  # prevent recursion
    instance.cache_remote_image()
    post_save.connect(event_post_save, sender=sender)
post_save.connect(event_post_save, sender=Event)


class Status:
    def __init__(self, code, label):
        self.code = code
        self.label = label

STATUS = {
    'NR': Status('NOREG', 'Not Registered'),
    'EX': Status('EX', 'Excused'),
    'PR': Status('PR/EX', 'Present or Excused'),
    'AB': Status('ABS', 'Absent')
}


class RegistrationManager(models.Manager):
    def create_registration(self, event, student, block):
        # need to check if student already has an event on that date in this block, if so, modify.
        reg = self.create(event=event,
                          student=student,
                          block=block,
                          absent=event.is_keypad_initialized
        )
        return reg

    def get_for_user_block_date(self, student, block, event_date):
        qs = self.get_queryset()
        return qs.filter(student=student).filter(event__date=event_date).filter(block=block)

    # def all_registered_unexcused(self, event_date, block=None):
    #     """
    #     :param event_date:
    #     :param block: a list of blocks to check. If no block, then check all.
    #     :return: a queryset of students registered in the block (or all blocks)
    #     """
    #     registrations_qs = self.get_queryset().filter(event__date=event_date)
    #     students = User.objects.all().filter(is_staff=False, is_active=True)
    #
    #     # get dictionary of students
    #     students_list = students.values('id', 'username')
    #
    #     return None

    def count_registered(self, date, block=None):
        qs = self.get_queryset().filter(event__date=date)
        if block:
            qs = qs.filter(block=block)
        return qs.count()


    def registration_check(self, event_date, homeroom_teacher=None):
        """
        :param event_date:
        :param homeroom_teacher: if not provided, will return all students
        :return: a list of student dicts, including their events for each block and excuses, if any
        """

        registrations_qs = self.get_queryset().filter(event__date=event_date).select_related('event', 'block', 'student')
        students = User.objects.filter(is_staff=False, is_active=True).select_related('profile', 'profile__homeroom_teacher')
        # excuses_qs = Excuse.objects.all_excused_on_day(date=event_date)

        if homeroom_teacher:
            students = students.filter(profile__homeroom_teacher=homeroom_teacher)
            registrations_qs = registrations_qs.filter(student__profile__homeroom_teacher=homeroom_teacher)

        students_dict = students.values('id',
                                        'username',
                                        'first_name',
                                        'last_name',
                                        'profile__grade',
                                        'profile__homeroom_teacher',
                                        'profile__permission',
                                        )

        for student_dict in students_dict:
            user_regs_qs = registrations_qs.filter(student_id=student_dict['id'])

            student = User.objects.get(id=student_dict['id'])
            excuses = student.excuse_set.all().date(event_date)
            for excuse in excuses:
                for block in excuse.blocks.filter(active=True):
                    student_dict[block.constant_string() + "_excuse"] = excuse.reason

            # provide homeroom teacher's name instead of id
            if student_dict['profile__homeroom_teacher']:
                hr_teacher = User.objects.get(id=student_dict['profile__homeroom_teacher'])
                student_dict['profile__homeroom_teacher'] = hr_teacher.get_full_name()

            blocks = Block.objects.active()
            for block in blocks:
                event_str = None
                event_url = "#"
                try:
                    reg = user_regs_qs.get(block=block)
                    event_str = str(reg.event)
                    event_url = str(reg.event.get_absolute_url())
                except ObjectDoesNotExist:
                    pass
                except MultipleObjectsReturned:
                    regs = user_regs_qs.filter(block=block)
                    event_str = "CONFLICT: "
                    for reg in regs:
                        event_str += str(reg.event) + "; "
                        event_url = reg.event.get_absolute_url()

                student_dict[block.constant_string()] = event_str
                student_dict[block.constant_string() + "_url"] = event_url

        return students_dict


    def all_attendance(self, event_date, reg_only=False):
        '''

        :param event_date:
        :param reg_only:
        :return: A list of absent student dictionaries
        [
            {...}, # student profile model info
            {'Block1': attendance},
            {'Block1': registered_event},
            {'Block2': attendance},
            {'Block2': registered_event},
        ]
        '''
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
                                   'profile__email',
                                   'profile__homeroom_teacher',
                                   'profile__permission',
                                   )
        students_list = list(students)

        # get queryset with events? optimization for less hits on db
        qs = self.get_queryset().filter(
            event__date=event_date,
        )

        for student_dict in students_list:
            user_regs_qs = qs.filter(student_id=student_dict['id'])

            # provide homeroom teacher's name instead of id
            if student_dict['profile__homeroom_teacher']:
                hr_teacher = User.objects.get(id=student_dict['profile__homeroom_teacher'])
                student_dict['profile__homeroom_teacher'] = hr_teacher.get_full_name()

            for block in Block.objects.active():
                check_if_excused = False
                try:
                    reg = user_regs_qs.get(block=block)
                    if reg.absent and not reg_only:
                        student_dict[block.constant_string()] = STATUS['AB'].code
                        check_if_excused = True
                    else:
                        student_dict[block.constant_string()] = STATUS['PR'].code

                    title = reg.event.title
                    student_dict[block.constant_string() + "_EVENT"] = title[:22] + "..." if len(title) > 25 else title

                except ObjectDoesNotExist:  # not registered
                    student_dict[block.constant_string() + "_EVENT"] = "NONE"
                    student_dict[block.constant_string()] = STATUS['NR'].code
                    check_if_excused = True

                # Check if they were excused?
                if check_if_excused:
                    student = User.objects.get(id=student_dict['id'])
                    excuses = student.excuse_set.all().date(event_date).in_block(block)
                    if excuses:
                        student_dict[block.constant_string()] = STATUS['EX'].code

        return students

    def attendance(self, flex_date):
        return self.get_queryset().filter(event__date=flex_date,
                                          student__is_active=True,
                                          student__is_staff=False,
                                          absent=True,
                                          )


class Registration(models.Model):

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    updated_timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)
    created_timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    absent = models.BooleanField(default=False)
    late = models.BooleanField(default=False)

    objects = RegistrationManager()

    class Meta:
        # order_with_respect_to = 'event'
        unique_together = ("event", "student", "block")

    def __str__(self):
        return str(self.student) + ": " + str(self.event)

    def is_same(self, event, block=None):
        # if the event is F1_AND_F2 then block is irrelevant
        if block and event.multi_block_event != Event.F1_AND_F2:
            return True if self.event == event and self.block == block else False
        else:  # check for match in all blocks.
            return True if self.event == event else False

    def is_conflict(self, event, block=None, regs_count=None, user=None, event_date=None, ):
        """
        :param event:
        :param block:
        :param user: if None assume the same user
        :param event_date: if None assume the same date
        :return: True if the event & block conflicts with this registration
        """
        #print(regs_count)
        reason = None
        already_reg = False
        if (user and self.student is not user) or (event_date and event_date != self.event.date):
            reason = None  # not same student or not same date
        else:
            if (block and self.is_same(event, block)) or \
                    (event.is_single_block() and self.is_same(event)) or \
                    (block is None and self.event.multi_block_event == Event.F1_XOR_F2 and self.is_same(event)):
                reason = "You are already registered for this event."
                already_reg = True
            elif self.event == event and self.event.multi_block_event == Event.F1_XOR_F2:
                reason = "You are already registered for this event in another block.  " \
                         "This event only allows registration in one block."
                already_reg = False
            elif self.event.both_required() or event.both_required() or \
                    (event.is_single_block() and self.block == event.blocks.filter(active=True)[0]) or \
                    (regs_count == 2):
                reason = "This event conflicts with another event you are already registered for. " \
                    "You will need to remove the conflicting event before you can register for this one."
                # this event occurs in the same block (or multi block AND)
            elif self.block == block:
                if self.event.multi_block_event == Event.F1_OR_F2 or self.event.multi_block_event == Event.F1_XOR_F2:
                    reason = "You are already registered for a different event in %s.  " \
                             "If you want to register for this event in another block, select the other block's tab " \
                             "at the top of this list." % str(block)
                else:
                    reason = "You are already registered for a different event in %s." % str(block)
            # elif block is None:  # check all blocks
            #     print("cehcking all blocks for event: " + str(event) + " in block: " + str(block))
            #     # need to check if this registration conflicts with single block events.
            #     # Do it recursively by checking both blocks
            #     for block in Block.objects.active():
            #         reason = self.is_conflict(event, block, user, event_date)
            #         if reason is not None:
            #             break
            #         # else keep going and check more blocks for conflicts.

        return already_reg, reason

    def past_cut_off(self):
        return self.event.is_registration_closed(self.block)
