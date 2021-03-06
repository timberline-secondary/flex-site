from datetime import timedelta
from django import forms
from django.contrib.auth.models import User
from django.forms import widgets
from django.forms.widgets import CheckboxSelectMultiple
from django.urls import reverse, reverse_lazy
from django_select2.forms import Select2Widget, Select2MultipleWidget, ModelSelect2MultipleWidget
from django.utils.safestring import mark_safe

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Event, Registration, Location, Category, Block


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = (
            "room_number",
            "name",
        )


class PlainTextWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        return mark_safe(value) if value is not None else '-'


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = (
            "absent",
            "late",
            # "excuse",
            # "student",
        )

    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)  # call base class
        # could be None if a student has dropped between the form loading and saving attendance.
        # not sure why the cascade delete hasn't deleted this registration though....
        # print (self.instance.student)
        try:
            self.first_name = self.instance.student.first_name
            self.last_name = self.instance.student.last_name
            self.student_number = self.instance.student.username
            self.permission = self.instance.student.profile.permission
        except User.DoesNotExist:
            # print("Student dropped")
            pass


class AttendanceFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        save_both = kwargs.pop('save_both', False)
        super(AttendanceFormSetHelper, self).__init__(*args, **kwargs)
        self.form_class = 'form-inline'
        self.form_id = 'attendance-form'
        # self.field_template = 'bootstrap3/layout/inline_field.html'
        self.template = 'events/attendance_table_inline_formset.html'

        btn_text = 'Save Attendance'
        if save_both:
            btn_text += ' (for both blocks)'
        else:
            btn_text += ' (for this block only)'

        self.add_input(Submit('submit', btn_text))


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


# http://stackoverflow.com/questions/28068168/django-adding-an-add-new-button-for-a-foreignkey-in-a-modelform
class RelatedFieldWidgetCanAdd(widgets.Select):

    def __init__(self, related_model, related_url=None, *args, **kw):

        super(RelatedFieldWidgetCanAdd, self).__init__(*args, **kw)

        if not related_url:
            rel_to = related_model
            info = (rel_to._meta.app_label, rel_to._meta.object_name.lower())
            related_url = 'admin:%s_%s_add' % info

        # Be careful that here "reverse" is not allowed
        self.related_url = related_url

    def render(self, name, value, *args, **kwargs):
        self.related_url = reverse(self.related_url)
        output = [super(RelatedFieldWidgetCanAdd, self).render(name, value, *args, **kwargs)]
        output.append('<a href="%s" class="add-another" id="add_id_%s"> ' % (self.related_url, name))
        output.append('<i class="fa fa-plus"></i> Add new</a> (this will reset your form)')
        return mark_safe(''.join(output))


class LocationModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_detailed_name()


class CategoryModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        # print(Event._meta.get_field('category').help_text)
        return "%s (%s)" % (obj.name, obj.description)


class EventForm(forms.ModelForm):
    location = LocationModelChoiceField(
        queryset=Location.objects.all(),
        widget=RelatedFieldWidgetCanAdd(Location, 'events:location_create'),
    )
    category = CategoryModelChoiceField(
        queryset=Category.objects.all(),
        help_text=Event._meta.get_field('category').help_text,
        initial=Category.get_default(),  # opportunity
    )

    duplicate = forms.IntegerField(
        label='Duplicate to future weeks',
        required=False,
        initial=0,
        max_value=10,
        min_value=0,
        help_text="If 1 or more, a duplicate of this event will be created for this number of weeks beyond the event "
                  "date. 0 = no duplicates, 1 = one duplicate, etc.  Each of these events will be unaware of each "
                  "other, and will have to be edited individually.  I suggest you save new events without "
                  "duplications first, to ensure it appears how you want it; then edit the event and change this "
                  "number to create the duplicates.",
    )

    blocks = forms.ModelMultipleChoiceField(
        queryset=Block.objects.active(),
        widget=CheckboxSelectMultiple,
    )

    class Meta:
        model = Event
        fields = [
            "date",
            "title",
            "blocks",
            "multi_block_event",
            "facilitators",
            "location",
            "max_capacity",
            "category",
            "description",
            "competencies",
            "description_image_file",
            "description_link",
            "registration_cut_off",
            "allow_registration_after_event_has_started"
            # "allow_facilitators_to_modify",
        ]
        widgets = {
            'facilitators': UserCustomTitleWidget,
            'blocks': CheckboxSelectMultiple,
            'competencies': CheckboxSelectMultiple,
            # 'location': RelatedFieldWidgetCanAdd(Location, reverse_lazy('events:location_create')),
            # 'location': RelatedFieldWidgetCanAdd(Location, 'events:location_create'),
        }

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        if Block.objects.single_block():
            self.fields.pop('blocks')
            self.fields.pop('multi_block_event')

