import csv
from datetime import date, datetime

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers import json
from django.forms import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DeleteView
from profiles.models import Profile
from .models import Event, default_event_date, Registration, Block
from .forms import EventForm, AttendanceForm, AttendanceFormSetHelper, RegistrationForm


@staff_member_required
def event_create(request):
    form = EventForm(request.POST or None)

    if form.is_valid():
        event = form.save(commit=False)
        event.creator = request.user
        event.save()
        form.save_m2m()
        messages.success(request, "Successfully Created")
        return HttpResponseRedirect(event.get_absolute_url())

    context = {
        "title": "Create Event",
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


@staff_member_required
def event_manage(request):
    # date_query = request.GET.get("date", str(default_event_date()))
    # d = datetime.strptime(date_query, "%Y-%m-%d").date()

    queryset = Event.objects.filter(facilitators=request.user)
    # Event.objects.all_for_facilitator(request.user)
    context = {
        # "date_filter": date_query,
        # "date_object": d,
        "title": "Your Events",
        "object_list": queryset,
        # "date_filter": d,
    }
    return render(request, "events/event_management.html", context)


def event_list(request):

    date_query = request.GET.get("date", str(default_event_date()))
    d = datetime.strptime(date_query, "%Y-%m-%d").date()

    flex1 = Block.objects.get_flex_1()
    flex2 = Block.objects.get_flex_2()

    if request.user.is_authenticated():
        # Find if the user already has an event for this day and block.
        # If he does, the start with that instance, else start a new instance
        try:
            user_reg = Registration.objects.get(student=request.user, block=flex1, event__date=d)
        except ObjectDoesNotExist:
            user_reg = Registration(student=request.user, block=flex1)  # Event will be set by form
        form_flex1 = RegistrationForm(request.POST or None,
                                      date=d, block=flex1,
                                      instance=user_reg,
                                      prefix='flex1')

        try:
            user_reg = Registration.objects.get(student=request.user, block=flex2, event__date=d)
        except ObjectDoesNotExist:
            user_reg = Registration(student=request.user, block=flex2)  # Event will be set by form
        form_flex2 = RegistrationForm(request.POST or None,
                                       date=d, block=flex2,
                                       instance=user_reg,
                                       prefix='flex2')

    else:
        form_flex1 = None
        form_flex2 = None

    if request.method == 'POST':
        if form_flex1.is_valid() and form_flex2.is_valid():
            form_flex1.save()
            form_flex2.save()
            return redirect("events:registrations_list")

    queryset = Event.objects.filter(date=d, category__visible_in_event_list=True)
    context = {
        "date_filter": date_query,
        "date_object": d,
        "title": "List",
        "object_list": queryset,
        # "register_form": form,
        "form_flex1": form_flex1,
        "form_flex2": form_flex2,
    }
    return render(request, "events/event_list.html", context)


@staff_member_required
def event_update(request, id=None):
    event = get_object_or_404(Event, id=id)

    form = EventForm(request.POST or None, instance=event)

    # not valid?
    if form.is_valid():
        event = form.save(commit=False)
        event.save()
        form.save_m2m()
        messages.success(request, "Successfully Updated")
        return HttpResponseRedirect(event.get_absolute_url())

    context = {
        "title": event.title,
        "event": event,
        "form": form,
        "btn_value": "Save"
    }
    return render(request, "events/event_form.html", context)


@staff_member_required
def event_copy(request, id=None):
    new_event = get_object_or_404(Event, id=id)
    new_event.pk = None  # autogen a new primary key (quest_id by default)
    new_event.date = None
    new_event.blocks = new_event

    form = EventForm(request.POST or None, instance=new_event)

    # not valid?
    if form.is_valid():
        event = form.save()

        messages.success(request, "New event created")
        return HttpResponseRedirect(event.get_absolute_url())

    context = {
        "title": new_event.title,
        "event": new_event,
        "form": form,
        "btn_value": "Save"
    }
    return render(request, "events/event_form.html", context)


@staff_member_required
def event_delete(request, id=None):
    event = get_object_or_404(Event, id=id)
    event.delete()
    messages.success(request, "Successfully deleted")
    return redirect("events/events:list")


@method_decorator(staff_member_required, name='dispatch')
class EventDelete(DeleteView):
    model = Event
    success_url = reverse_lazy('events:manage')


@login_required
def register(request):
    data = json.loads(request.body)
    print(data)
    return redirect("events:list")


@login_required
def staff_locations(request):
    date_query = request.GET.get("date", str(default_event_date()))
    d = datetime.strptime(date_query, "%Y-%m-%d").date()

    users = User.objects.all().filter(is_staff=True).values('id', 'first_name', 'last_name')
    users = list(users)

    events = Event.objects.all().filter(date=d)

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


@staff_member_required
def generate_synervoice_csv(request, d):
    def blocks_absent(s):
        str = ""
        if 'FLEX1' in s:
            str += s['FLEX1']
        if 'FLEX2' in s:
            str += s['FLEX2']
        return str

    d_str = d.strftime("%y%m%d")

    attendance_data = Registration.objects.all_attendance(d)

    absent_data = [s for s in attendance_data if len(s) > 7]

    # https://docs.djangoproject.com/en/1.10/howto/outputting-csv/
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="synervoice.csv"'

    writer = csv.writer(response)
    for s in absent_data:
        writer.writerow([s['last_name'] + ", " + s['first_name'],
                         s['username'],
                         s['profile__grade'],
                         s['profile__email'],
                         d_str,
                         blocks_absent(s),
                       ])

    return response


@staff_member_required
def synervoice(request):
    if request.method == "POST":
        event_date = request.POST.get("date")
        d = datetime.strptime(event_date, "%Y-%m-%d").date()
        return generate_synervoice_csv(request, d)

    return render(request, "events/synervoice.html")


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


@staff_member_required
def registrations_all(request):
    queryset = Registration.objects.all()
    context = {
        "object_list": queryset
    }
    return render(request, "events/registration_all.html", context)


@login_required
def registrations_delete(request, id=None):
    reg = get_object_or_404(Registration, id=id)
    reg.delete()
    messages.success(request, "Successfully Deleted")
    return redirect("events:registrations_manage")


@login_required
def registrations_manage(request):
    queryset = Registration.objects.filter(student=request.user)
    context = {
        "object_list": queryset
    }
    return render(request, "events/registration_list.html", context)


@staff_member_required
def event_attendance(request, id=None, block_id=None):
    event = get_object_or_404(Event, id=id)
    if block_id:
        active_block = get_object_or_404(Block, id=block_id)
    else:
        active_block = event.blocks.all()[0]

    queryset1 = Registration.objects.filter(event=event, block=active_block)

    # https://docs.djangoproject.com/en/1.9/topics/forms/modelforms/#model-formsets
    AttendanceFormSet1 = modelformset_factory(Registration, form=AttendanceForm, extra=0)
    helper = AttendanceFormSetHelper()

    if request.method =="POST":
        formset1 = AttendanceFormSet1(
            request.POST, request.FILES,
            queryset=queryset1,
            prefix='flex1'
        )
        if formset1.is_valid():
            formset1.save()

    else:
        formset1 = AttendanceFormSet1(queryset=queryset1, prefix='flex1')


    context = {
        "object_list_1": queryset1,
        "event": event,
        "formset1": formset1,
        "helper": helper,
        "active_block": active_block,
    }
    return render(request, "events/attendance.html", context)


@staff_member_required
def registrations_homeroom(request, user_id=None):
    date_query = request.GET.get("date", str(default_event_date()))
    d = datetime.strptime(date_query, "%Y-%m-%d").date()

    if user_id:
        homeroom_teacher = get_object_or_404(User, id=user_id)
    else:
        homeroom_teacher = request.user
    profile_queryset = Profile.objects.select_related('user').filter(homeroom_teacher=homeroom_teacher)
    profile_queryset.annotate()

    students = Registration.objects.homeroom_registration_check(d, homeroom_teacher)

    context = {
        "object_list": profile_queryset,
        "students": students,
        "teacher": homeroom_teacher,
        "date_filter": date_query,
        "date_object": d,
    }
    return render(request, "events/homeroom_list.html", context)
