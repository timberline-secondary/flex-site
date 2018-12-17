from datetime import datetime

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Prefetch
from django.shortcuts import render, redirect, get_object_or_404

from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DeleteView

from excuses.forms import ExcuseForm
from excuses.models import Excuse
from flex.utils import default_event_date


@staff_member_required
def excuse_list(request, block_id=None):
    date_query = request.GET.get("date", str(default_event_date()))
    d = datetime.strptime(date_query, "%Y-%m-%d").date()

    queryset = Excuse.objects.current(d).prefetch_related(
        Prefetch('students', queryset=User.objects.order_by('last_name')),
        'reason')
    # queryset = Excuse.objects.all()
    # queryset.prefetch_related('students', 'blocks')
    context = {
        "date_filter": date_query,
        "date_object": d,
        "object_list": queryset,
    }
    return render(request, "excuses/excuse_list.html", context)


@staff_member_required
def excuse_create(request):
    form = ExcuseForm(request.POST or None)

    if form.is_valid():
        excuse = form.save()
        excuse.save()

        msg = "New excuse list created for <i>%s</i> from: %s to %s" % \
              (excuse.reason, excuse.first_date, excuse.last_date)

        messages.success(request, msg)

        return redirect('excuses:excuse_list')

    context = {

        "title": "Excuse Students",
        "form": form,
        "btn_value": "Save"
    }
    return render(request, "excuses/excuse_form.html", context)


@staff_member_required
def excuse_edit(request, id):
    instance = get_object_or_404(Excuse, id=id)

    form = ExcuseForm(request.POST or None, instance=instance)

    if form.is_valid():
        excuse = form.save()
        excuse.save()
        msg = "Excuse list updated for <i>%s</i> from: %s to %s" % \
              (excuse.reason, excuse.first_date, excuse.last_date)
        messages.success(request, msg)
        return redirect('excuses:excuse_list')

    context = {
        "title": "Edit Excused Students",
        "form": form,
        "btn_value": "Update",
        "delete_btn": True,
        "excuse": instance,
    }
    return render(request, "excuses/excuse_form.html", context)


@method_decorator(staff_member_required, name='dispatch')
class ExcuseDelete(DeleteView):
    model = Excuse
    success_url = reverse_lazy('excuses:excuse_list')
