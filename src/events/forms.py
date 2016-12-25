from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import CheckboxSelectMultiple
from django_select2.forms import Select2Widget, Select2MultipleWidget, ModelSelect2MultipleWidget
from django.utils.safestring import mark_safe

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from tinymce.widgets import TinyMCE

from .models import Event, Registration


class PlainTextWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        return mark_safe(value) if value is not None else '-'


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = (
            "absent",
            "late",
            "excused",
            # "student",
        )

    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)  # call base class
        self.first_name = self.instance.student.first_name
        self.last_name = self.instance.student.last_name
        self.student_number = self.instance.student.username


class AttendanceFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(AttendanceFormSetHelper, self).__init__(*args, **kwargs)
        self.form_class = 'form-inline'
        self.form_id = 'attendance-form'
        # self.field_template = 'bootstrap3/layout/inline_field.html'
        self.template = 'events/attendance_table_inline_formset.html'

        self.add_input(Submit('submit', 'Save Attendance'))


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['event']

        widgets = {
            'student': PlainTextWidget,
        }

    def __init__(self, *args, **kwargs):
        date = kwargs.pop('date')
        block = kwargs.pop('block')
        super(RegistrationForm, self).__init__(*args, **kwargs)

        if date and block:
            flex_qs = Event.objects.all_for_date(event_date=date, block=block)
            self.fields['event'].queryset = flex_qs

            DOM_id = "event-" + str(block)
            self.fields['event'].widget.attrs.update({'id': DOM_id, })
            self.fields['event'].label = "Selection for " + str(block)
            # self.fields['event'].widget.attrs.update({'readonly': 'readonly', })


class RegistrationFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(RegistrationFormSetHelper, self).__init__(*args, **kwargs)
        self.form_class = 'form-inline'
        # self.field_template = 'bootstrap3/layout/inline_field.html'
        # self.template = 'events/attendance_table_inline_formset.html'

        self.add_input(Submit('submit', 'Save Selections'))


class UserCustomTitleWidget(ModelSelect2MultipleWidget):
    model = User

    search_fields = [
        'first_name__istartswith',
        'last_name__istartswith',
        'username__istartswith',
    ]

    def label_from_instance(self, obj):
        return obj.get_full_name().upper()


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "date",
            "title",
            "blocks",
            "multi_block_event",
            "facilitators",
            "category",
            "location",
            "description",
            "description_link",
            "allow_facilitators_to_modify",
        ]
        widgets = {
            'description': TinyMCE(mce_attrs={'theme': 'simple',
                                              }),
            'facilitators': UserCustomTitleWidget,
            'blocks': CheckboxSelectMultiple,
        }

    # def __init__(self, *args, **kwargs):
    #     super(EventForm, self).__init__(*args, **kwargs)
    #
    #     self.fields["description"].widget = TinyMCE(attrs={'theme': 'advanced', })
    #     # self.fields["facilitators"].widget.attrs.update({'class': 'chosen-select', })
