import csv
from collections import OrderedDict
from datetime import date, datetime

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers import json
from django.db import models
from django.db.models import Sum, Count
from django.forms import modelformset_factory, model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import DeleteView

from excuses.models import Excuse
from profiles.models import Profile
from .models import Event, default_event_date, Registration, Block
from .forms import EventForm, AttendanceForm, AttendanceFormSetHelper, RegistrationForm, LocationForm

#Hello it's Me (Nandini)
@staff_member_required
def location_create(request):
    form = LocationForm(request.POST or None)

    if form.is_valid():
        loc = form.save()
        messages.success(request, "New location added: <b>%s (%s)</b>" % (loc, loc.name))
        return redirect('events:create')

    context = {
        "title": "Add new location",
        "form": form,
        "btn_value": "Save"
    }
    return render(request, "events/location_form.html", context)


@staff_member_required
def event_create(request):
    form = EventForm(request.POST or None)

    if form.is_valid():
        event = form.save(commit=False)
        event.creator = request.user
        event.save()
        form.save_m2m()

        msg = "New event created for %s: <b>%s</b>" % (event.date, event.title)

        num_duplicates = form.cleaned_data['duplicate']
        if num_duplicates:
            dupe_dates = event.copy(num_duplicates, user=request.user)
            # http://stackoverflow.com/questions/9052433/overriding-default-format-when-printing-a-list-of-datetime-objects
            msg += "; duplicates made for %s." % ', '.join(map(str, dupe_dates))

        messages.success(request, msg)

        if not event.cache_remote_image():
            messages.warning(request, "Failed to properly cache your image.  Don't worry about it for now... unless "
                                      "you didn't provide an image link, in which case please let Tylere know!")

        block_id = event.blocks.all()[0].id
        date_query = event.date
        return redirect("%s?date=%s" % (reverse('events:list_by_block', args=(block_id,)), date_query))

    context = {
        "title": "Create Event",
        "form": form,
        "btn_value": "Save"
    }
    return render(request, "events/event_form.html", context)


@staff_member_required
def event_update(request, id=None):
    event = get_object_or_404(Event, id=id)
    has_registrants = event.registration_set.all().exists()

    if has_registrants:
        regs_dict_by_block = {}  # empty dict
        for block in Block.objects.all():
            regs_dict_by_block[block.id] = block.registration_set.filter(event=event).count()

    form = EventForm(request.POST or None, instance=event)

    # not valid?
    if form.is_valid():
        new_max_capacity = form.cleaned_data['max_capacity']
        if has_registrants and new_max_capacity < max(regs_dict_by_block.values()):
            messages.warning(request,
                             "<i class='fa fa-warning'></i> You can't reduce the max capacity (%d) below the current number of registered students "
                             "in a block (%d).  If this is a problem, you can delete the event to boot "
                             " all students, then recreate it with the capacity you want."
                             "" % (new_max_capacity, max(regs_dict_by_block.values())))

        else:
            event = form.save(commit=False)
            event.save()
            form.save_m2m()

            msg = "Edits saved for %s: <b>%s</b>" % (event.date, event.title)
            num_duplicates = form.cleaned_data['duplicate']
            if num_duplicates:
                dupe_dates = event.copy(num_duplicates, user=request.user)
                # http://stackoverflow.com/questions/9052433/overriding-default-format-when-printing-a-list-of-datetime-objects
                msg += "; duplicates made for %s." % ', '.join(map(str, dupe_dates))

            messages.success(request, msg)

            if not event.cache_remote_image():
                messages.warning(request, "Failed to properly cache your image.  Don't worry about it for now... unless "
                                          "you didn't provide an image link, in which case please let Tylere know!")

            block_id = event.blocks.all()[0].id
            date_query = event.date
            return redirect("%s?date=%s" % (reverse('events:list_by_block', args=(block_id,)), date_query))

    context = {
        "title": event.title,
        "delete_btn": True,
        "event": event,
        "form": form,
        "btn_value": "Save",
        "has_registrants": has_registrants,
        # "regs_dict_by_block": regs_dict_by_block,
    }
    return render(request, "events/event_form.html", context)


@staff_member_required
def event_copy(request, id):
    new_event = get_object_or_404(Event, id=id)

    blocks = new_event.blocks.all()
    facilitators = new_event.facilitators.all()
    competencies = new_event.competencies.all()

    new_event.pk = None  # autogen a new primary key (quest_id by default)
    new_event.date = None

    d = {'blocks': blocks,
         'facilitators': facilitators,
         'competencies': competencies,
         }

    form = EventForm(request.POST or None, instance=new_event, initial=d)

    # not valid?
    if form.is_valid():
        event = form.save()

        msg = "New event created for %s: <b>%s</b>" % (event.date, event.title)

        num_duplicates = form.cleaned_data['duplicate']
        if num_duplicates:
            dupe_dates = event.copy(num_duplicates, user=request.user)
            # http://stackoverflow.com/questions/9052433/overriding-default-format-when-printing-a-list-of-datetime-objects
            msg += "; duplicates made for %s." % ', '.join(map(str, dupe_dates))

        if not event.cache_remote_image():
            messages.warning(request, "Failed to properly cache your image.  Don't worry about it for now... unless "
                                      "you didn't provide an image link, in which case please let Tylere know!")

        messages.success(request, msg)

        block_id = event.blocks.all()[0].id
        date_query = event.date
        return redirect("%s?date=%s" % (reverse('events:list_by_block', args=(block_id,)), date_query))

    context = {
        "title": new_event.title,
        "event": new_event,
        "form": form,
        "btn_value": "Save"
    }
    return render(request, "events/event_form.html", context)


def event_detail(request, id=None):
    instance = get_object_or_404(Event, id=id)
    context = {
        "title": instance.title,
        "event": instance,
    }
    return render(request, "events/event_detail.html", context)


# @staff_member_required
# def event_delete(request, id=None):
#     event = get_object_or_404(Event, id=id)
#     registrants = event.registration_set
#     event.delete()
#     if registrants is not None:
#         messages.warning(request, "You deleted an event that already had students registered for it.  "
#                                   "You may want to notify the students: " + registrants)
#     else:
#         messages.success(request, "Successfully deleted")
#     return redirect("events/events:list")


@method_decorator(staff_member_required, name='dispatch')
class EventDelete(DeleteView):
    model = Event
    success_url = reverse_lazy('events:manage')


@staff_member_required
def event_manage(request):
    # date_query = request.GET.get("date", str(default_event_date()))
    # d = datetime.strptime(date_query, "%Y-%m-%d").date()

    queryset = Event.objects.filter(facilitators=request.user)

    # for event in queryset:
    #     for block in event.blocks.all():
    #         event.attendance = {}
    #         event.attendance = event.registration_set.filter().count()

    context = {
        # "date_filter": date_query,
        # "date_object": d,
        "title": "Your Events",
        "object_list": queryset,
        # "date_filter": d,
    }
    return render(request, "events/event_management.html", context)


@staff_member_required
def stats(request):
    date_query = request.GET.get("date", str(default_event_date()))
    d = datetime.strptime(date_query, "%Y-%m-%d").date()
    blocks = Block.objects.all()

    registration_stats = {"Slots": {}, "Registrations": {}} #, "Excused": {}}

    for block in blocks:
        registration_stats["Slots"][block] = Event.objects.all_for_date(d, block=block).aggregate(Sum('max_capacity'))
        registration_stats["Slots"][block] = registration_stats["Slots"][block]["max_capacity__sum"]
        registration_stats["Registrations"][block] = Registration.objects.filter(event__date=d, block=block).count()
        # registration_stats["Excused"][block] = Excuse.objects.all_on_date(d, block=block).count()

    context = {
        "date_filter": date_query,
        "date_object": d,
        "stats": registration_stats,
        "blocks": blocks,
        # "active_block": active_block,
    }

    return render(request, "events/stats.html", context)


def get_registration_stats(date, grade=None, students=None):
    """
    :param date:
    :param grade:
    :param students:
    :return: An OrderedDict like this:
    {["Count" : 123, "# Flex-1": 32, "% Flex-1": 26, ... "# Flex-n": 132, "% Flex-n": 26, "# all": 132, "% all": 26 ]}
    """
    blocks = Block.objects.all()

    if students is None:
        students = User.objects.filter(is_active=True, is_staff=False)

    if grade:
        students = students.filter(profile__grade=grade)

    total_students = students.count()

    reg_stats = OrderedDict()  # empty dict

    reg_stats["count"] = total_students

    # for each block, find the number of excused students and registered students, subtract from the total to get
    # number of non-registered students
    for block in blocks:
        excused_students = Excuse.objects.students_excused_on_date(date, block, students=students)
        # print("Grade: " + str(grade) + ", Block: " + str(block))

        not_registered_students = students.exclude(registration__event__date=date, registration__block=block)
        registered_students = students.filter(registration__event__date=date, registration__block=block)

        # remove registered students from the excused students, if there are any, so they aren't counted twice
        # This is needed because excused student can still register for events if they want
        excused_students = excused_students.difference(registered_students)

        num_excused = excused_students.count()
        num_not_registered = not_registered_students.count() - num_excused

        # reg_stats["Ex " + str(block)] = num_excused
        reg_stats["# " + str(block)] = num_not_registered
        reg_stats["% " + str(block)] = int(num_not_registered/total_students * 100) if total_students else "NA"


    # count the number of students who have registered for NO events
    # reg_both_count = students.annotate(
    #     num_of_articles=models.Count(
    #                 models.Case(models.When(registration__event__date=date, then=1), output_field=models.IntegerField())
    #     )
    # ).filter(num_of_articles=2).count()

    # excused = Excuse.objects.students_excused_on_date(date, blocks, students=students)
    # reg_stats["Ex all"] = excused.count()
    # count = total_students - reg_both_count
    # reg_stats["# all"] = count
    # reg_stats["% all"] = int(count/total_students * 100)

    return reg_stats


def get_attendance_stats(date, grade=None):
    blocks = Block.objects.all()
    students = User.objects.filter(is_active=True, is_staff=False)
    if grade:
        students = students.filter(profile__grade=grade)
    total_students = students.count()

    att_stats = OrderedDict()  # empty dict

    att_stats["count"] = total_students

    # for each block, find the number of absent students who are not excused
    for block in blocks:
        absent_students = students.filter(registration__event__date=date,
                                          registration__block=block,
                                          registration__absent=True
                                          )
        excused_students = Excuse.objects.students_excused_on_date(date, block, students=students)
        # remove excused students
        absent_students = absent_students.difference(excused_students)

        num_absent = absent_students.count()

        att_stats["Ex " + str(block)] = excused_students.count()
        att_stats["# " + str(block)] = num_absent
        att_stats["% " + str(block)] = int(num_absent / total_students * 100)

    return att_stats


@staff_member_required
def stats2(request):
    date_query = request.GET.get("date", str(default_event_date()))
    d = datetime.strptime(date_query, "%Y-%m-%d").date()
    blocks = Block.objects.all()

    registration_stats = OrderedDict()  # empty dicts
    attendance_stats = OrderedDict()

    for grade in range(9, 13):
        registration_stats[str(grade)] = get_registration_stats(d, grade=grade)
        attendance_stats[str(grade)] = get_attendance_stats(d, grade=grade)

    registration_stats["All"] = get_registration_stats(d)
    attendance_stats["All"] = get_attendance_stats(d)

    context = {
        "date_filter": date_query,
        "date_object": d,
        "registration_stats": registration_stats,
        "attendance_stats": attendance_stats,
        "blocks": blocks,
    }

    return render(request, "events/stats2.html", context)

###############################################
#
#       ATTENDANCE VIEWS
#
################################################

@staff_member_required
def event_attendance_keypad(request, id, block_id=None, absent_value=True):
    event = get_object_or_404(Event, id=id)

    registrations = event.registration_set.all()
    registrations.update(absent=absent_value)
    event.is_keypad_initialized = absent_value
    event.save()
    return event_attendance(request, id, block_id)


@staff_member_required
def event_attendance_keypad_disable(request, id, block_id=None):
    return event_attendance_keypad(request, id, block_id, absent_value=False)


@staff_member_required
def event_attendance(request, id=None, block_id=None):
    event = get_object_or_404(Event, id=id)
    blocks = event.blocks.all()

    multi_block_save_option = blocks.count() > 1 and \
                              (event.multi_block_event == Event.F1_AND_F2 or event.multi_block_event == Event.F1_OR_F2)

    if block_id:
        active_block = get_object_or_404(Block, id=block_id)
    else:
        active_block = blocks[0]

    queryset1 = Registration.objects.filter(event=event, block=active_block).order_by('student__last_name')

    # https://docs.djangoproject.com/en/1.9/topics/forms/modelforms/#model-formsets
    AttendanceFormSet1 = modelformset_factory(Registration,
                                              form=AttendanceForm,
                                              extra=0)
    helper = AttendanceFormSetHelper()

    if request.method =="POST":
        formset1 = AttendanceFormSet1(
            request.POST, request.FILES,
            queryset=queryset1,
            prefix='flex1'
        )
        if formset1.is_valid():
            formset1.save()
            messages.success(request, "Attendance saved for <b>%s</b> during <b>%s</b>" % (event, active_block))

    else:
        formset1 = AttendanceFormSet1(queryset=queryset1, prefix='flex1')

    context = {
        "object_list_1": queryset1,
        "event": event,
        "formset1": formset1,
        "helper": helper,
        "active_block": active_block,
        "multi_block_save_option": multi_block_save_option,
    }
    return render(request, "events/attendance.html", context)

@staff_member_required()
def event_list_export(request):
    date_query = request.GET.get("date", str(default_event_date()))
    d = datetime.strptime(date_query, "%Y-%m-%d").date()

    queryset = Event.objects.all()

    queryset = Event.objects.all().filter(
        date=d,
    ).select_related('location').prefetch_related('competencies')

    context = {
        "object_list": queryset,
        "date_filter": date_query,
        "date_object": d,
    }
    return render(request, "events/event_list_export.html", context)


def event_list(request, block_id=None):
    date_query = request.GET.get("date", str(default_event_date()))
    d = datetime.strptime(date_query, "%Y-%m-%d").date()

    if block_id:
        active_block = get_object_or_404(Block, id=block_id)
    else:
        active_block = Block.objects.all()[0]

    blocks = Block.objects.all()
    blocks_json = serializers.serialize('json', blocks, fields=('id', 'name', ))

    queryset = active_block.event_set.filter(
        date=d,
        category__visible_in_event_list=True
    ).select_related('location').prefetch_related('competencies')

    registrations = {}
    excuses_dict = {}
    if request.user.is_authenticated() and not request.user.is_staff:
        # Build a dictionary of user's registrations for this day:
        # {block_name: event,}
        for block in blocks:
            registrations[block] = {}
            try:
                reg = Registration.objects.get(student=request.user, block=block, event__date=d)
            except Registration.DoesNotExist:
                reg = None

                # Are they excused?
                excuses = request.user.excuse_set.all().date(d).in_block(block)
                if excuses:
                    registrations[block]["excuse"] = excuses[0]

            registrations[block]["reg"] = reg

    for event in queryset:
        event.attendance = event.registration_set.filter(block=active_block).count()
        if request.user.is_authenticated():
            event.available, event.already, event.explanation = event.is_available(request.user, active_block)
        else:
            event.available = True

    context = {
        "date_filter": date_query,
        "date_object": d,
        "title": "List",
        "object_list": queryset,
        "registrations": registrations,
        "excuses": excuses_dict,
        "blocks_json": blocks_json,
        "blocks": blocks,
        "active_block": active_block,
    }
    return render(request, "events/event_list.html", context)

###############################################
#
#      STAFF LOCATIONS
#
################################################

@login_required
def staff_locations(request):
    date_query = request.GET.get("date", str(default_event_date()))
    d = datetime.strptime(date_query, "%Y-%m-%d").date()

    users = User.objects.filter(is_staff=True, is_active=True).values('id', 'first_name', 'last_name')
    users = list(users)

    events = Event.objects.filter(date=d)

    for user in users:
        user_events = events.filter(facilitators__id=user['id'])

        for block in Block.objects.all():
            try:
                block_events = user_events.filter(blocks=block)
                user[block.constant_string()] = block_events
            except ObjectDoesNotExist:
                user[block.constant_string()] = None

    context = {
        "date_filter": date_query,
        "date_object": d,
        "users": users,
    }
    return render(request, "events/staff.html", context)

###############################################
#
#       SYNERVOICE VIEWS
#
################################################


@staff_member_required
def generate_synervoice_csv(request, d, no_reg_only=False):
    def blocks_absent(s):
        str = ""
        sep = ""
        if 'FLEX1' in s:
            str += s['FLEX1']
            sep = " "
        if 'FLEX2' in s:
            str += sep + s['FLEX2']
        return str

    d_str = d.strftime("%y%m%d")
    attendance_data = Registration.objects.all_attendance(d, no_reg_only)
    # A 9h column exists if the student was absent or didn't register
    # maybe check for key instead?
    absent_data = [s for s in attendance_data if len(s) > 8]

    filename = "synervoice"
    if no_reg_only:
        filename += "-not-registered"
    else:
        filename += "-attendance"
    filename += "-%s.csv" % d_str

    # https://docs.djangoproject.com/en/1.10/howto/outputting-csv/
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + filename

    writer = csv.writer(response)

    writer.writerow(["Student Name",
                     "Student Number",
                     "Homeroom Teacher",
                    "Grade",
                     "Home Phone",
                     "Home Email",
                     "Date",
                     "Flex-1 Status",
                     "Flex-1 Event",
                     "Flex-2 Status",
                     "Flex-2 Event",
                     ])

    for s in absent_data:
        # hack to remove excused students
        if "EX" in s['FLEX1'] and "EX" in s['FLEX2']:
            # if present: "PRESENT OR EXCUSED" so also caught
            pass
        else:
            writer.writerow([s['last_name'] + ", " + s['first_name'],
                             s['username'],
                             s['profile__homeroom_teacher'],
                             s['profile__grade'],
                             s['profile__phone'],
                             s['profile__email'],
                             d_str,
                             s['FLEX1'],
                             s['FLEX1_EVENT'],
                             s['FLEX2'],
                             s['FLEX2_EVENT'],
                             # blocks_absent(s),  # Add F regardless of whether absent or didn't register, one or both
                             ])

    return response


@staff_member_required
def synervoice(request):
    date_query = request.GET.get("date", str(default_event_date()))
    d = datetime.strptime(date_query, "%Y-%m-%d").date()

    if request.method == "POST":
        event_date = request.POST.get("date")
        d = datetime.strptime(event_date, "%Y-%m-%d").date()
        no_reg_only = False
        if request.POST.get('registration'):
            no_reg_only = True

        return generate_synervoice_csv(request, d, no_reg_only)

    context = {
        "date_filter": date_query,
        "d": d,
    }

    return render(request, "events/synervoice.html", context)


###############################################
#
#       REGISTRATION VIEWS
#
################################################
@login_required
def registrations_list(request):
    queryset = Registration.objects.filter(student=request.user)
    context = {
        "object_list": queryset
    }
    return render(request, "events/registration_list.html", context)


@login_required
def registrations_list(request):
    queryset = Registration.objects.filter(student=request.user)
    context = {
        "object_list": queryset
    }
    return render(request, "events/registration_list.html", context)


@login_required
def register(request, id, block_id):
    date_query = request.GET.get("date", str(default_event_date()))
    event = get_object_or_404(Event, id=id)

    available = True  # preset to True, then check both blocks, a conflict will switch this to False

    # block_id = 0 indicates register for all block in an optional OR event.
    both_on_or = False
    if block_id == '0':
        both_on_or = True
        for block in event.blocks.all():
            if available:
                available, already, reason = event.is_available(request.user, block)
                block_id = block.id  # need to give it a valid id for page redirection. 0 not valid!
    else:
        block = get_object_or_404(Block, id=block_id)
        available, already, reason = event.is_available(request.user, block)

    block_text = ""
    if available:
        if event.both_required() or both_on_or:
            for block in event.blocks.all():
                Registration.objects.create_registration(event=event, student=request.user, block=block)
                block_text += str(block) + " "

        else:
            Registration.objects.create_registration(event=event, student=request.user, block=block)
            block_text = str(block)

        messages.success(request, "Successfully registered for <b>%s</b> during <b>%s</b> " % (event, block_text))
    else:
        messages.warning(request, "<i class='fa fa-exclamation-triangle'></i> %s" % reason)
    return redirect("%s?date=%s" % (reverse('events:list_by_block', args=(block_id,)), date_query))


@login_required
def registrations_delete(request, id=None):
    reg = get_object_or_404(Registration, id=id)
    if reg.event.both_required():
        # maybe try/except instead?
        # Delete all records of this event (i.e. for all blocks)
        regs = Registration.objects.filter(event=reg.event, student=reg.student)
        regs.delete()
    else:
        reg.delete()
    messages.success(request, "You've been removed from <b>%s</b>" % reg.event)

    # Return to page that got us here.
    # http://stackoverflow.com/questions/12758786/redirect-return-to-same-previous-page-in-django
    # Don't do this with forms/POST
    if request.META:  # this can be turned off, so need to check
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('events:registrations_list')


@login_required
def registrations_manage(request):
    queryset = Registration.objects.filter(student=request.user)
    context = {
        "object_list": queryset
    }
    return render(request, "events/registration_list.html", context)


################################
#
#  Homeroom Views
#
###############################

@staff_member_required
def registrations_homeroom(request, employee_number=None):
    date_query = request.GET.get("date", str(default_event_date()))
    d = datetime.strptime(date_query, "%Y-%m-%d").date()

    if employee_number:
        homeroom_teacher = get_object_or_404(User, username=employee_number)
    else:
        homeroom_teacher = request.user

    students = Registration.objects.registration_check(d, homeroom_teacher)

    context = {
        "heading": "Homeroom Students for " + homeroom_teacher.get_full_name(),
        "students": students,
        "date_filter": date_query,
        "date_object": d,
        "title": "Homeroom",
    }
    return render(request, "events/homeroom_list.html", context)


@staff_member_required
def registrations_all(request):
    date_query = request.GET.get("date", str(default_event_date()))
    d = datetime.strptime(date_query, "%Y-%m-%d").date()

    students = Registration.objects.registration_check(d)

    context = {
        "heading": "All Student Registrations",
        "students": students,
        "date_filter": date_query,
        "date_object": d,
        "include_homeroom_teacher": 'true',
        "title": "All Students",
    }
    return render(request, "events/homeroom_list.html", context)

@staff_member_required
def stats_staff(request):
    date_query = request.GET.get("date", str(default_event_date()))
    d = datetime.strptime(date_query, "%Y-%m-%d").date()
    blocks = Block.objects.all()

    staff = User.objects.filter(is_staff=True, is_active=True)
    #staff = User.objects.filter(is_staff=True, is_active=True).prefetch_related('')

    # we only need stats on staff with homeroom students
    staff = staff.annotate(Count('students')).filter(students__count__gt=0)

    staff_stats = OrderedDict()  # empty dict

    for teacher in staff:
        staff_stats[teacher] = get_registration_stats(d, students=User.objects.filter(profile__in=teacher.students.all()))

    context = {
        "heading": "Staff Stats",
        "staff": staff,
        "date_filter": date_query,
        "date_object": d,
        "title": "Staff Stats",
        "blocks": blocks,
        "staff_stats": staff_stats,
    }
    return render(request, "events/stats_staff.html", context)
