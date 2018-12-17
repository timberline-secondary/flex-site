from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models import Count

from flex.utils import default_event_date


class ExcuseReason(models.Model):
    reason = models.CharField(max_length=50)
    flex_activity = models.BooleanField(default=False, help_text="Check this if the student is still conducting"
                                                                 " an activity compliant with the Flex course.")

    def __str__(self):
        return self.reason

    class Meta:
        ordering = ['reason']


class ExcuseQuerySet(models.QuerySet):
    def date(self, date):
        return self.filter(first_date__lte=date, last_date__gte=date)

    def in_block(self, block):
        return self.filter(blocks=block)

    def in_blocks_exact(self, blocks):
        # https://stackoverflow.com/questions/16324362/django-queryset-get-exact-manytomany-lookup

        # print(len(blocks))
        # print(self)


        excuse_qs = self.annotate(count=Count('blocks')).filter(count=len(blocks))

        # print(excuse_qs)
        # for exc in excuse_qs:
        #     print(exc)
        #     print(exc.blocks)
        #     print("*********")

        for block in blocks:
            # print (block)
            excuse_qs = excuse_qs.filter(blocks=block)
            # print(excuse_qs)
        return excuse_qs

    def for_student(self, user):
        return self.filter(students=user)


class ExcuseManager(models.Manager):
    def get_queryset(self):
        return ExcuseQuerySet(self.model, using=self._db)

    def current(self, as_of_date=default_event_date()):
        """ Filters out excuses that have past (has an end date beyond the as_of_date)
        """
        return self.get_queryset().filter(last_date__gte=as_of_date)

    def all_on_date(self, date, block=None):
        qs = self.get_queryset().date(date)
        # qs.filter(blocks__id=block.id)
        # for excuse in qs:
        #     print(block)
        #     print(excuse.blocks.all())

        return qs

    def students_excused_on_date(self, date, block, students=None):
        """
        :param date: excuses covering this date
        :param students: a queryset of students to check
        :param blocks: a queryset of Block objects
        :return: a queryset of students who are excused on this date, for the given blocks
        """

        # https://stackoverflow.com/questions/45062238/django-getting-a-list-of-foreign-key-objects
        if not students:
            students = User.objects.filter(is_active=True, is_staff=False)

        return students.filter(excuse__in=self.get_queryset().date(date).in_block(block))


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