# https://docs.djangoproject.com/en/1.11/howto/custom-template-tags/#inclusion-tags
from django import template

from utilities.models import MenuItem

register = template.Library()

@register.inclusion_tag('list_of_links.html')
def menu_list():
    links = MenuItem.objects.filter(visible=True)
    return {'links': links}
