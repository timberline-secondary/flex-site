from django import forms


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

