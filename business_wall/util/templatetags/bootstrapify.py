from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

def format_invalid_feedback(field):
    invalid_feedback = f'<div class="invalid-feedback"><ul id="{field.id_for_label}-errors">'
    for error in list(field.errors):
        invalid_feedback += '<li>{}</li>'.format(error)
    invalid_feedback += '</ul></div>'
    return invalid_feedback

def format_label(field):
    hidden = "hidden" if "hidden" in field.as_widget() else ""
    return f'<label for="{field.id_for_label}" {hidden}>{field.label}</label>'

def format_input(field, classes="", attrs=""):
    widget = field.as_widget()
    matches = re.findall("<\w+ ", widget)
    if matches:
        input = widget
        for match in set(matches):

            input = input.replace(match, f'{match}{attrs} class="form-{"check" if "checkbox" in widget else "control"} {classes} {"is-invalid" if len(list(field.errors)) else ""}"')
        return input
    else:
        return ""

def format_help_text(field):
    return f'<div class="text-muted">{field.help_text}</div>'

@register.filter(is_safe=True)
def bootstrapify_field(field, picker_id=""):
    input = format_input(field)
    invalid_feedback = format_invalid_feedback(field)
    label = format_label(field)
    help_text = format_help_text(field)
    return mark_safe('<div class="">{}{}{}{}</div>'.format(label, input, help_text, invalid_feedback))

@register.filter(is_safe=True)
def bootstrapify_datepicker_field(field, form_id):
    attrs = f'data-target="#{form_id} #{field.id_for_label}" data-toggle="datetimepicker"'
    input = format_input(field, classes="datetimepicker-input", attrs=attrs)
    invalid_feedback = format_invalid_feedback(field)
    label = format_label(field)
    help_text = format_help_text(field)
    return mark_safe('<div class="">{}{}{}{}</div>'.format(label, input, help_text, invalid_feedback))

@register.filter(is_safe=True)
def bootstrapify_errors(errors):
    errorlist = ''
    for error in errors:
        errorlist += (
            '<div class="alert alert-warning alert-dismissible fade show" role="alert">'
                + error +
                '<button type="button" class="close" data-dismiss="alert" aria-label="Close">'
                '<span aria-hidden="true">&times;</span>'
              '</button>'
            '</div>'
        )
    return mark_safe(errorlist)
