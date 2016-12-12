from crispy_forms.bootstrap import StrictButton
from django import forms
from django.forms import modelformset_factory, ModelChoiceField, TextInput
from django.forms.widgets import CheckboxSelectMultiple
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from django.utils.safestring import mark_safe

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML, MultiField, Div

from .models import Event, Block, Registration


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
            "student",
        )

        widgets = {
            'student': PlainTextWidget,
        }



class AttendanceFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(AttendanceFormSetHelper, self).__init__(*args, **kwargs)
        self.form_class = 'form-inline'
        # self.field_template = 'bootstrap3/layout/inline_field.html'
        self.template = 'events/attendance_table_inline_formset.html'

        self.add_input(Submit('submit', 'Save'))


class RegisterForm(forms.Form):
    flex_1_event_choice = forms.ModelChoiceField(queryset=Event.objects.all(), required=False)
    flex_2_event_choice = forms.ModelChoiceField(queryset=Event.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        event_date = kwargs.pop('event_date')
        super(RegisterForm, self).__init__(*args, **kwargs)

        if event_date:
            flex1 = Block.objects.get_flex_1()
            flex1_qs = Event.objects.all_for_date(event_date=event_date, block=flex1)
            flex2 = Block.objects.get_flex_2()
            flex2_qs = Event.objects.all_for_date(event_date=event_date, block=flex2)
            self.fields['flex_1_event_choice'].queryset = flex1_qs
            self.fields['flex_2_event_choice'].queryset = flex2_qs


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "date",
            "blocks",
            "multi_block_event",
            "title",
            "description",
            "category",
            "location",
            "facilitators",
            "allow_facilitators_to_modify",
        ]
        widgets = {
            'description': SummernoteWidget,
        }

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)

        self.fields["blocks"].widget = CheckboxSelectMultiple()
        self.fields["facilitators"].widget.attrs.update({'class': 'chosen-select',})
