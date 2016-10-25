from django.template.defaulttags import register

@register.filter
def get_form_model_name(model):
    return model._meta.verbose_name.title()

@register.filter
def get_item(dictionary, key):
	return dictionary.get(key)