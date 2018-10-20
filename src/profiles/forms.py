from django import forms
from django.contrib.auth.models import User
from django_select2.forms import ModelSelect2MultipleWidget

from profiles.models import Profile


class UserImportForm(forms.Form):
    SEMESTERS = (
        ('SEM1', 'SEM1'),
        ('SEM2', 'SEM2'),
    )
    semester = forms.ChoiceField(choices=SEMESTERS, initial='SEM1',
                                 help_text='This will ensure the proper homeroom teacher when updating students')

    student_csv_file = forms.FileField(label="Student Data File",
                                       required=False,
                                       help_text="A csv file without headings in the format: id, first_name, last_name, "
                                                 "homeroom_teacher_id, grade, term, phone, email")

    staff_csv_file = forms.FileField(label="Staff Data File",
                                     required=False,
                                     help_text="A csv file without headings in the format: id, first_name, last_name, position, email")


class StudentsCustomTitleWidget(ModelSelect2MultipleWidget):
    model = Profile
    queryset = Profile.objects.all_active_students()

    search_fields = [
        'user__first_name__istartswith',
        'user__last_name__istartswith',
        'user__username__istartswith',
    ]

    def label_from_instance(self, obj):
        return obj.user.get_full_name().upper()


class PermissionForm(forms.Form):

    students_permission_granted = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.all_active_students(),
        widget=StudentsCustomTitleWidget,
        help_text="List students with permission to attend low risk excursions during flex.",
        required=False,
    )
    students_permission_rejected = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.all_active_students(),
        widget=StudentsCustomTitleWidget,
        help_text="List students whose parents have had rejected permission for low risk excursions.",
        required=False,
    )
