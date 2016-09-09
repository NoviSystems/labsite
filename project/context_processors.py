from django.conf import settings

def navbar_context(request):
    return {
        'current_app': getattr(request.resolver_match, 'app_name', None),
        'labsite_apps': settings.LABSITE_APPS,
    }
