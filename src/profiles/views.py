from django.shortcuts import render
import csv
# Create your views here.
from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404, redirect
from registration.forms import User

from .models import Profile


class PublisherList(ListView):
    model = Profile


def mass_user_import(request):
    path = ""
    with open(path) as f:
        reader = csv.reader(f)
        for row in reader:

            homeroom_teacher = row[2]

            _, created = Profile.objects.get_or_create(
                first_name=row[0],
                last_name=row[1],
                homeroom_teacher=homeroom_teacher
            )
            # creates a tuple of the new object or
            # current object and a boolean of if it was created


def home_room(request, user_id=None):
    if user_id:
        homeroom_teacher = get_object_or_404(User, id=user_id)
    else:
        homeroom_teacher = request.user
    queryset = Profile.objects.filter(homeroom_teacher=homeroom_teacher)
    print(queryset)
    context = {
        "object_list": queryset,
        "teacher": homeroom_teacher,
    }
    return render(request, "profiles/homeroom_list.html", context)
