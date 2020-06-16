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
from django.utils import timezone

from .models import Profile
from .forms import UserImportForm, PermissionForm


######################################
#
#   PROFILE VIEWS
#
######################################
# class ProfileList(ListView):
#     model = Profile

@staff_member_required()
def reset_password_to_default(request, id):
    student = get_object_or_404(User, id=id)
    this_user = request.user

    if student.profile.homeroom_teacher == this_user or this_user.is_superuser:
        student.password = make_password("wolf")
        student.save()
        messages.success(request, "Password has been reset to \"wolf\" for %s." % student.get_full_name())
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
    num_deactivated = 0
    form = UserImportForm(request.POST or None, request.FILES or None)

    positions_to_import = ["TEACHER", "VICE-PRINCIPAL", "PRINCIPAL", "EA", "TOC", "DIST YOUTH WRK", "DIST YOUTH WRK", "CERLICAL"]  
    # currently not included: ED ASSISTANT, IT TECHNICIAN, CUSTODIAL
    grades_to_ignore = ["AD", "HS", "RG", "NS"]  # ADult grad, Home Schooled, Returning Grad, Non Student

    if form.is_valid():
        if 'staff_csv_file' in request.FILES:
            file = request.FILES['staff_csv_file']
            reader = csv.reader(codecs.iterdecode(file, 'utf-8'))
            staff_import = True
            for row in reader:
                # check for blank rows, proper number of fields, and staff positions
                if row and len(row) == 5 and row[3] in positions_to_import:
                    try:
                        username = row[0]
                        int(username)  # will throw an error if not an integer

                        qs = User.objects.all()

                        # check if user exists, else create new user
                        if username and not qs.filter(username=username).exists():
                            user = User.objects.create_user(
                                username=username,
                                password="wolf",
                                last_name=row[1].strip().upper(),
                                first_name=row[2].strip().upper(),
                                email=row[4].strip(),
                                is_staff=True,
                            )
                            new_staff_list.append(user)
                    except ValueError:  # ID is not an integer
                        pass

        if 'student_csv_file' in request.FILES:
            update_start_time = timezone.now()

            file = request.FILES['student_csv_file']
            semester = form.cleaned_data['semester']

            reader = csv.reader(codecs.iterdecode(file, 'utf-8'))
            student_import = True
            count = 0

            users_qs = User.objects.all()

            # important columns in csv
            student_number_heading = "Login Student Number"
            sn_regex_string = r"^(9[789])(\d{5})$"  # 7 digits beginning in 99 98 or 97
            first_name_heading = "Usual first name"
            last_name_heading = "Usual surname"
            email_heading = "StudentEmail"
            homeroom_teacher_heading = "Teacher ID"
            phone_heading = "StudentHomePhoneNumber"
            contact_email_heading = "EmergencyContactEmail1"
            grade_heading = "Grade"

            student_number_col = None
            first_name_col = None
            last_name_col = None
            email_col = None
            homeroom_teacher_col = None
            phone_col = None
            contact_email_col = None
            grade_col = None

            for row in reader:

                # skip empty rows and rows without proper number of fields
                if row and len(row) >= 8:

                    if email_heading in row:  # Heading row
                        try:
                            student_number_col = row.index(student_number_heading)
                            first_name_col = row.index(first_name_heading)
                            last_name_col = row.index(last_name_heading)
                            email_col = row.index(email_heading)
                            homeroom_teacher_col = row.index(homeroom_teacher_heading)
                            phone_col = row.index(phone_heading)
                            contact_email_col = row.index(homeroom_teacher_heading)
                            grade_col = row.index(grade_heading)
                        except ValueError:
                            student_errors.append({'error': "Expected column header not found", 'row': row})
                            break

                    else:  # Student data row
                        if not email_col:  # then we haven't got a header row yet
                            student_errors.append({'error': "Heading row not found", 'row': row})
                            break

                        # Get username from student email and check if the user exists
                        email = row[email_col]
                        username = email.split("@")[0].strip().lower()
                        first_name = row[first_name_col].strip().upper()
                        last_name = row[last_name_col].strip().upper()
                        homeroom_teacher = row[homeroom_teacher_col].strip()
                        student_number = row[student_number_col].strip()
                        phone = row[phone_col].strip()
                        contact_email = row[contact_email_col].strip()
                        grade = row[grade_col].strip()

                        # validate username/email
                        if not username:
                            student_errors.append({'error': "No email/username found for student.  Account not created.", 'row': row})
                            break

                        # validate student number
                        # if not re.match(sn_regex_string, student_number):
                        #     student_errors.append({'error': "Student number doesn't match 99 pattern", 'row': row})

                        # validate homeroom teacher
                        try:  # sometimes homeroom id shows up as 0, which doesn't exist
                            homeroom_teacher = User.objects.get(username=homeroom_teacher)
                        except User.DoesNotExist:
                            student_errors.append({'warning': "Homeroom teacher with ID '" + homeroom_teacher +
                                                                "' not recognized", 'row': row})
                            homeroom_teacher = None

                        # clean grade
                        if not grade:  # needs an int so empty string is bad
                            grade = None
                        else:
                            try:
                                int(grade)
                            except ValueError:  # grade is text, not an integer
                                student_errors.append({'warning': "Grade not recognized", 'row': row})
                                grade = None

                        # change blank strings to None
                        if not phone:
                            phone = None
                        if not contact_email:
                            contact_email = None

                        
                        # Check if user exists with first.last as username
                        try: 
                            user = users_qs.get(username=username)
                        except User.DoesNotExist: 
                            # Check if their student number is a valid user (old usernames were student numbers)
                            try:
                                user = User.objects.get(username=student_number)
                                user.username = username  # update username to first.last as username
                                student_errors.append({'info': "Username updated from {} to {}".format(student_number, username), 'row': row})
                            except User.DoesNotExist:
                                # they are a new user!
                                user = User.objects.create_user(
                                    username=username,
                                    password="wolf",
                                )
                                new_student_list.append(user.id)
                        
                        # We have a user object now.  Update names and set active:
                        user.is_active = True
                        user.first_name = first_name
                        user.last_name = last_name
                        user.save()

                        # A profile is created automatically when a new user is created.  Update it.
                        # But sometimes errors cause a user to be created without a profile.  So just in case:
                        profile, created = Profile.objects.get_or_create(user=user)
                        profile.homeroom_teacher = homeroom_teacher
                        profile.grade = grade
                        profile.phone = phone
                        profile.email = contact_email
                        profile.save()
                        count += 1

            # passed to template
            new_student_list = User.objects.filter(id__in=new_student_list)

            # Activate/Deactive students
            # If a student's profile wasn't updated, then they were not on the list and are no longer active.
            students_qs = User.objects.filter(is_staff=False)
            inactive_students_qs = students_qs.filter(profile__updated__lt=update_start_time)
            num_deactivated = inactive_students_qs.update(is_active=False)


            # else:
            #     # students should have one entry for each semester, only use semester indicated in form
            #     # also, ignore students with off grade entries
            #     # SEM 1 or SEM1, so remove spaces before comparison
            #     # row_semester = row[5].replace(" ", "")
            #     # if (row_semester == semester or row[5] == "LINEAR") and row[4] not in grades_to_ignore:
            #     #     username = row[0]
            #     #     first_name = row[1]
            #     #     last_name = row[2]
            #     #     homeroom_teacher = row[3]
            #     #     grade = row[4]

    context = {
        "new_staff_list": new_staff_list,
        "staff_import": staff_import,
        "new_student_list": new_student_list,
        "student_import": student_import,
        "student_errors": student_errors,
        "num_deactivated": num_deactivated,
        "form": form,
    }
    return render(request, "profiles/profile_imports.html", context)


@user_passes_test(lambda u: u.is_superuser)
def permissions_update(request):

    students = Profile.objects.all_active_students()
    form = PermissionForm(request.POST or None)

    if form.is_valid():
        granted = form.cleaned_data['students_permission_granted']
        rejected = form.cleaned_data['students_permission_rejected']

        granted.update(permission=True)
        rejected.update(permission=False)

        msg = "Student permission records updated."
        messages.success(request, msg)

        return redirect('profiles:permissions_update')


    context = {
        "student_list": students,
        "form": form,
    }
    return render(request, "profiles/permission_update.html", context)

