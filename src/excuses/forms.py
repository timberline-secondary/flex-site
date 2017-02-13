from django import forms
from django.contrib.auth.models import User
from django.forms import CheckboxSelectMultiple
from django.forms import widgets
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_select2.forms import ModelSelect2MultipleWidget

from events.forms import RelatedFieldWidgetCanAdd
from excuses.models import ExcuseReason, Excuse


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


class StudentsCustomTitleWidget(ModelSelect2MultipleWidget):
    model = User

    search_fields = [
        'first_name__istartswith',
        'last_name__istartswith',
        'username__istartswith',
    ]

    def label_from_instance(self, obj):
        return obj.get_full_name().upper()


class ExcuseForm(forms.ModelForm):
    reason = forms.ModelChoiceField(
        queryset=ExcuseReason.objects.all(),
        widget=RelatedFieldWidgetCanAdd(ExcuseReason),
    )

    class Meta:
        model = Excuse
        fields = [
            "first_date",
            "last_date",
            "blocks",
            "reason",
            "students",
        ]
        widgets = {
            'students': StudentsCustomTitleWidget,
            'blocks': CheckboxSelectMultiple,
        }

