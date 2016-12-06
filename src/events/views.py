from datetime import date, datetime

from django.contrib import messages
from django.core.serializers import json
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from .models import Event, default_event_date, Registration, Block
from .forms import EventForm, RegisterForm


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
    return render(request, "event_form.html", context)


def event_detail(request, id=None):
    instance = get_object_or_404(Event, id=id)
    context = {
        "title": instance.title,
        "event": instance,
    }
    return render(request, "event_detail.html", context)


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
    return render(request, "event_management.html", context)


def event_attendance(request, id=None):
    event = get_object_or_404(Event, id=id)
    queryset = Registration.objects.filter(event=event)

    context = {
        "object_list": queryset,
        "event": event,
    }
    return render(request, "attendance.html", context)


def event_list(request):

    date_query = request.GET.get("date", str(default_event_date()))
    d = datetime.strptime(date_query, "%Y-%m-%d").date()

    form = RegisterForm(request.POST or None, event_date=d)

    if request.method == 'POST':
        if form.is_valid():
            event1 = form.cleaned_data['flex_1_event_choice']
            event2 = form.cleaned_data['flex_2_event_choice']

            if event1:
                Registration.objects.create_registration(
                    student=request.user,
                    event=event1,
                    block=Block.objects.get_flex_1(),
                )
            if event2:
                Registration.objects.create_registration(
                    student=request.user,
                    event=event2,
                    block=Block.objects.get_flex_2(),
                )
            return redirect("events:registrations_list")

    queryset = Event.objects.filter(date=d)
    context = {
        "date_filter": date_query,
        "date_object": d,
        "title": "List",
        "object_list": queryset,
        "register_form": form,
    }
    return render(request, "event_list.html", context)


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
    return render(request, "event_form.html", context)


def event_delete(request, id=None):
    event = get_object_or_404(Event, id=id)
    event.delete()
    messages.success(request, "Successfully Deleted")
    return redirect("events:list")


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
    return render(request, "registration_list.html", context)

def registrations_manage(request):
    #date_query = request.GET.get("date", str(default_event_date()))
    #d = datetime.strptime(date_query, "%Y-%m-%d").date()
    queryset = Registration.objects.filter(student=request.user)
    context = {
        "object_list": queryset
    }
    return render(request, "registration_list.html", context)
