from typing import override

from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView

from .models import LogEntry, Project, TechnicalStrength


class RootPage (TemplateView):
    template_name = "portfolio/index.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["projects"] = Project.objects.filter(active=True).prefetch_related("stack")
        context["technical_strengths"] = TechnicalStrength.objects.all()

        return context


class LoggingView(TemplateView):
    template_name = "portfolio/logging.html"

    @override
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        log_list = LogEntry.objects.select_related('project').prefetch_related('stack').order_by('-date')
        paginator = Paginator(log_list, 10)
        context["page_obj"] = paginator.get_page(1)
        context["log_count"] = LogEntry.objects.count()
        
        return context


def single_log(request, log_id):
    if request.method == "GET":
        import markdown
        log = get_object_or_404(LogEntry.objects.select_related('project').prefetch_related('stack'), id=log_id)
        
        # Parse markdown to HTML
        log.html_content = markdown.markdown(log.content, extensions=['fenced_code', 'tables'])

        context = {
            "log": log
        }

        return render(
            request,
            "portfolio/_log.html",
            context,
            content_type="text/html"
        )

    return HttpResponse(status=405)

def log_list(request):
    if request.method == "GET":
        queryset = LogEntry.objects.select_related('project').prefetch_related('stack').order_by('-date')
        paginator = Paginator(queryset, 10)

        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, "portfolio/_log_nav_partial.html", {
            "page_obj": page_obj
        })

    return HttpResponse(status=405)
