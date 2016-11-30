from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget

from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "date",
            "blocks",
            "both_required",
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
