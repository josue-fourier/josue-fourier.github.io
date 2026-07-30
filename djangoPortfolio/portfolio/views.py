from django.views.generic import TemplateView

from .models import Project, TechnicalStrength


class RootPage (TemplateView):
    template_name = "portfolio/index.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["projects"] = Project.objects.filter(active=True)
        context["technical_strengths"] = TechnicalStrength.objects.all()

        return context
