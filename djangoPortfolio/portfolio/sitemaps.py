from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Project, LogEntry

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['root', 'log_list']

    def location(self, item):
        if item == 'root':
            return reverse('root')
        elif item == 'log_list':
            return '/logging/'

class ProjectSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return Project.objects.filter(active=True)
        
    def location(self, item):
        return reverse('project_detail', args=[item.id])

class LogEntrySitemap(Sitemap):
    priority = 0.9
    changefreq = 'weekly'

    def items(self):
        return LogEntry.objects.all().order_by('-date')

    def lastmod(self, obj):
        return obj.date

    def location(self, obj):
        return f'/logging/?log_id={obj.id}'
