from django.views.generic import TemplateView


class About(TemplateView):
    template_name = 'templates/pages/about.html'
