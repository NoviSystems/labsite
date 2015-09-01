from django.conf import settings


def navbar_context(request):
    return {
      'current_app': request.resolver_match.app_name,
      'labsite_apps': settings.LABSITE_APPS,
    }
