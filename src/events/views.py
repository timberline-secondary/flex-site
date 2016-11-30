
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from .models import Event, default_event_date
from .forms import EventForm


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
        "title": "Create a new Event",
        "form": form,
        "btn_value": "Create"
    }
    return render(request, "event_form.html", context)


def event_detail(request, id=None):
    instance = get_object_or_404(Event, id=id)
    context = {
        "title": instance.title,
        "event": instance,
    }
    return render(request, "event_detail.html", context)


def event_list(request):
    date_query = request.GET.get("date", str(default_event_date()))

    queryset = Event.objects.filter(date=date_query)
    context = {
        "date_filter": date_query,
        "title": "List",
        "object_list": queryset
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
        "btn_value": "Save Changes"
    }
    return render(request, "event_form.html", context)


def event_delete(request, id=None):
    event = get_object_or_404(Event, id=id)
    event.delete()
    messages.success(request, "Successfully Deleted")
    return redirect("events:list")
