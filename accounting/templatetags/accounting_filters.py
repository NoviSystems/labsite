from django.template.defaulttags import register


@register.filter
def get_form_model_name(form):
    return form._meta.model._meta.verbose_name.title()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
