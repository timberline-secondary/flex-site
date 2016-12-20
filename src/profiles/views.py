from datetime import datetime

from django.db import IntegrityError
from django.http import Http404
from events.models import default_event_date, Registration
from random import randint

from django.shortcuts import render
import csv

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404, redirect
from registration.forms import User

from .models import Profile


class ProfileList(ListView):
    model = Profile


def mass_user_import(request):
    # path = static("user_list.csv")
    path = "/home/couture/Developer/flex-site/static_cdn/user_list.csv"
    teachers = User.objects.all().filter(is_staff=True)

    with open(path) as f:
        reader = csv.reader(f)
        for row in reader:

            try:
                user = User.objects.create_user(
                    username=row[0],
                    password="123123",
                    first_name=row[1],
                    last_name=row[2],
                )
            except IntegrityError:  # user already exists
                user = get_object_or_404(User, username=row[0])

            random_index = randint(0, len(teachers) - 1)

            # even if new user NOT created, update profile data
            profile = get_object_or_404(Profile, user=user)
            profile.first_name = row[1]
            profile.last_name = row[2]
            profile.homeroom_teacher = teachers[random_index]
            profile.save()

        return redirect("profiles:list")

