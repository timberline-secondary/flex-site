import re
import codecs
import csv

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.http import Http404

from django.shortcuts import render, get_object_or_404, redirect

from .models import Profile
from .forms import UserImportForm


# class ProfileList(ListView):
#     model = Profile

@staff_member_required()
def reset_password_to_default(request, id):
    student = get_object_or_404(User, id=id)
    this_user = request.user

    if student.profile.homeroom_teacher is this_user or this_user.is_superuser:
        student.password = make_password("wolf")
        student.save()
        messages.success(request, 'Password reset to "wolf".')
        return redirect('events:registrations_homeroom')
    else:
        raise Http404("You are not this student's homeroom teacher.")


@user_passes_test(lambda u: u.is_superuser)
def mass_update(request):

    new_staff_list = []
    new_student_list = []
    student_errors = []
    staff_errors = []
    staff_import = False
    student_import = False
    form = UserImportForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        if 'staff_csv_file' in request.FILES:
            file = request.FILES['staff_csv_file']
            reader = csv.reader(codecs.iterdecode(file, 'utf-8'))
            staff_import = True
            for row in reader:
                if row:  # check for blank rows
                    username = row[0]
                    qs = User.objects.all()
                    # check if user exists, else create new user
                    if not qs.filter(username=username).exists():
                        user = User.objects.create_user(
                            username=username,
                            password="wolf",
                            first_name=row[1],
                            last_name=row[2],
                            is_staff=True,
                        )
                        new_staff_list.append(user)

        if 'student_csv_file' in request.FILES:
            file = request.FILES['student_csv_file']
            semester = form.cleaned_data['semester']

            reader = csv.reader(codecs.iterdecode(file, 'utf-8'))
            student_import = True
            count = 0
            for row in reader:

                sn_regex_string = r"^(9[789])(\d{5})$"

                # skip empty rows and rows without proper number of fields
                if row and len(row) == 8:
                    # check for student number
                    if not re.match(sn_regex_string, row[0]):
                        student_errors.append({'error': "Student number doesn't match pattern", 'row': row})
                    else:
                        # students should have one entry for each semester, only use semester indicated in form
                        if row[5] == semester:
                            username = row[0]
                            first_name = row[1]
                            last_name = row[2]
                            homeroom_teacher = row[3]
                            grade = row[4]
                            phone = row[6]
                            email = row[7]

                            # validate data
                            try:  # sometimes homeroom id shows up as 0, which doesn't exist
                                homeroom_teacher = User.objects.get(username=homeroom_teacher)
                            except User.DoesNotExist:
                                student_errors.append({'warning': "Homeroom teacher not recognized", 'row': row})
                                homeroom_teacher = None
                            if not grade:  # needs an int so empty string is bad
                                grade = None
                            if not phone:
                                phone = None
                            if not email:
                                email = None

                            qs = User.objects.all()
                            # check if user exists, else create new user
                            if not qs.filter(username=username).exists():
                                user = User.objects.create_user(
                                    username=username,
                                    password="wolf",
                                    first_name=first_name,
                                    last_name=last_name,
                                )
                                new_student_list.append(user.id)
                            else:
                                user = User.objects.get(username=username)

                            # A profile is created automatically when a new user is created.  Update it.
                            # But sometimes errors cause a user to be created without a profile.  So just in case:
                            profile, created = Profile.objects.get_or_create(user=user)
                            homeroom_teacher = homeroom_teacher
                            profile.homeroom_teacher = homeroom_teacher
                            profile.grade = grade
                            profile.phone = phone
                            profile.email = email
                            profile.save()
                            count += 1

            new_student_list = User.objects.all().filter(id__in=new_student_list)

    # student_import=True
    # new_student_list = User.objects.all().filter(is_staff=False)
    context = {
        "new_staff_list": new_staff_list,
        "staff_import": staff_import,
        "new_student_list": new_student_list,
        "student_import": student_import,
        "student_errors": student_errors,
        "form": form,
    }
    return render(request, "profiles/profile_imports.html", context)

