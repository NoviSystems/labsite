from django.views.generic.base import TemplateView


class LabsiteView(TemplateView):
	template_name = 'labsite.html'

	def get(self, request, *args, **kwargs):
		print "executed view"
		return super(LabsiteView, self).get(request, *args, **kwargs)
