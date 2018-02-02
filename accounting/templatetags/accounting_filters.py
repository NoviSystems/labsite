from django import template
from accounting.utils import format_currency

register = template.Library()


@register.filter
def get_form_model_name(form):
    return form._meta.model._meta.verbose_name.title()


@register.filter
def currency(value, decimal=True):
    return format_currency(value, decimal)
