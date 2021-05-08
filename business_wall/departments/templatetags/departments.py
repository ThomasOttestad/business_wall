from django import template
from departments.models import Department

register = template.Library()

@register.simple_tag(takes_context=True)
def get_departments(context):
    return Department.objects.all()
