from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget

from .models import Event, Block

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
        self.fields["facilitators"].widget.attrs.update({'class': 'chosen-select', })
