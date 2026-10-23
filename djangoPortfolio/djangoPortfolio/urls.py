"""
URL configuration for djangoPortfolio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""

from decouple import config
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView
from portfolio import views as portfolio_views
from portfolio.sitemaps import LogEntrySitemap, ProjectSitemap, StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "projects": ProjectSitemap,
    "logs": LogEntrySitemap,
}

urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url=settings.STATIC_URL + "portfolio/icons/favicon.ico", permanent=True)),
    path("health", portfolio_views.health_check, name="health_no_slash"),
    path("health/", portfolio_views.health_check, name="health"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="portfolio/robots.txt", content_type="text/plain"
        ),
    ),
    path(config("ADMIN_URL", default="brutally-amazing-portfolio/"), admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", portfolio_views.RootPage.as_view(), name="root_direct"),
    path("api/logs/<uuid:log_id>", portfolio_views.single_log, name="single_log"),
    path("api/logs/<uuid:log_id>/", portfolio_views.single_log, name="single_log_slash"),
    path("api/logs/list", portfolio_views.log_list, name="log_list"),
    path("project/<int:project_id>/", portfolio_views.project_detail, name="project_detail_fallback"),
    path("project/<int:project_id>", portfolio_views.project_detail, name="project_detail_fallback_no_slash"),
    path("api/telemetry/heartbeat/", portfolio_views.telemetry_heartbeat, name="telemetry_heartbeat"),
    path("api/telemetry/heartbeat", portfolio_views.telemetry_heartbeat, name="telemetry_heartbeat_no_slash"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path("", portfolio_views.RootPage.as_view(), name="root"),
    path("project/<int:project_id>/", portfolio_views.project_detail, name="project_detail"),
    path("project/<int:project_id>", portfolio_views.project_detail, name="project_detail_no_slash"),
)
