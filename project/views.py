from django.views.generic.base import TemplateView


class LabsiteView(TemplateView):
    template_name = 'base.html'

    def get(self, request, *args, **kwargs):
        return super(LabsiteView, self).get(request, *args, **kwargs)
