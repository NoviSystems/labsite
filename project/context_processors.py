from django.conf import settings


def navbar_context(request):
    app_name = getattr(request.resolver_match, 'app_name', None)
    app = next((
        app for app in settings.LABSITE_APPS
        if app['app_name'] == app_name
    ), None)

    return {
        'current_app': app,
        'labsite_apps': settings.LABSITE_APPS,
    }
