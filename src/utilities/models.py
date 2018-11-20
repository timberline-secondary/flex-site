from django.db import models

# Create your models here.
from django.utils.safestring import mark_safe


class MenuItem(models.Model):

    label = models.CharField(max_length=25, help_text="This is the text that will appear for the menu item.")
    fa_icon = models.CharField(max_length=50, default="link",
                               help_text=mark_safe("The Font Awesome icon to display beside the text. E.g. 'star-o'. "
                                                   "Options from <a target='_blank'"
                                                   "href='http://fontawesome.com/v4.7.0/icons/'>Font Awesome</a>."))
    url = models.URLField(help_text="The link.")
    open_link_in_new_tab = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0, help_text="Lowest will be at the top.")
    visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        target = 'target="_blank"' if self.open_link_in_new_tab else ''
        return '<a href="{0}" {1}>' \
               '<i class="fa fa-fw fa-{2}"></i>&nbsp;&nbsp;{3}' \
               '</a>'.format(self.url, target, self.fa_icon, self.label)



