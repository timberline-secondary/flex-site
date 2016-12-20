from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers import json
from django.forms import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from profiles.models import Profile
from .models import Event, default_event_date, Registration, Block
from .forms import EventForm, AttendanceForm, AttendanceFormSetHelper, RegistrationForm


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


def event_manage(request):

    # date_query = request.GET.get("date", str(default_event_date()))
    # d = datetime.strptime(date_query, "%Y-%m-%d").date()
    # queryset = request.user.event_set.all()
    queryset = Event.objects.filter(facilitators=request.user)
    # Event.objects.all_for_facilitator(request.user)
    context = {
        # "date_filter": date_query,
        # "date_object": d,
        "title": "Your Events",
        "object_list": queryset,
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

    queryset = Event.objects.filter(date=d)
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


def event_copy(request, id=None):
    new_event = get_object_or_404(Event, id=id)
    new_event.pk = None  # autogen a new primary key (quest_id by default)
    new_event.date = None

    form = EventForm(request.POST or None, instance=new_event)

    # not valid?
    if form.is_valid():
        event = form.save()

        messages.success(request, "Successfully Updated")
        return HttpResponseRedirect(event.get_absolute_url())

    context = {
        "title": new_event.title,
        "event": new_event,
        "form": form,
        "btn_value": "Save"
    }
    return render(request, "events/event_form.html", context)


def event_delete(request, id=None):
    event = get_object_or_404(Event, id=id)
    event.delete()
    messages.success(request, "Successfully Deleted")
    return redirect("events/events:list")


def register(request):
    data = json.loads(request.body)
    print(data)
    return redirect("events:list")


###############################################
#
#       REGISTRATION VIEWS
#
################################################

def registrations_list(request):
    #date_query = request.GET.get("date", str(default_event_date()))
    #d = datetime.strptime(date_query, "%Y-%m-%d").date()
    queryset = Registration.objects.filter(student=request.user)
    context = {
        "object_list": queryset
    }
    return render(request, "events/registration_list.html", context)

def registrations_all(request):
    #date_query = request.GET.get("date", str(default_event_date()))
    #d = datetime.strptime(date_query, "%Y-%m-%d").date()
    queryset = Registration.objects.all()
    context = {
        "object_list": queryset
    }
    return render(request, "events/registration_all.html", context)

def registrations_manage(request):
    #date_query = request.GET.get("date", str(default_event_date()))
    #d = datetime.strptime(date_query, "%Y-%m-%d").date()
    queryset = Registration.objects.filter(student=request.user)
    context = {
        "object_list": queryset
    }
    return render(request, "events/registration_list.html", context)


# def homeroom(request, id=None):
#     students = Profile.objects.all().filter(homeroom_teacher=request.user)
#     event = get_object_or_404(Event, id=id)
#     queryset = Registration.objects.filter(event=event)
#
#     context = {
#         "object_list": queryset,
#         "event": event,
#         "formset": formset,
#         "helper": helper,
#     }
#     return render(request, "events/homeroom.html", context)

def event_attendance(request, id=None, block_id=None):
    if block_id:
        block = get_object_or_404(Event, id=block_id)
    else:
        block = Block.objects.get_flex_2()
    event = get_object_or_404(Event, id=id)
    queryset = Registration.objects.filter(event=event, block=block)

    # https://docs.djangoproject.com/en/1.9/topics/forms/modelforms/#model-formsets
    AttendanceFormSet = modelformset_factory(Registration, form=AttendanceForm, extra=0)
    helper = AttendanceFormSetHelper()

    if request.method =="POST":
        formset = AttendanceFormSet(
            request.POST, request.FILES,
            queryset=queryset,
        )
        if formset.is_valid():
            formset.save()
    else:
        formset = AttendanceFormSet(queryset=queryset)

    context = {
        "object_list": queryset,
        "event": event,
        "formset": formset,
        "helper": helper,
    }
    return render(request, "events/attendance.html", context)


def registrations_homeroom(request, user_id=None):
    date_query = request.GET.get("date", str(default_event_date()))
    d = datetime.strptime(date_query, "%Y-%m-%d").date()
    # d = datetime.strptime("2016-11-30", "%Y-%m-%d").date()

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
