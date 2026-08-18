from django.contrib import admin

from .models import LogEntry, Project, TechnicalStrength

admin.site.register(Project)
admin.site.register(TechnicalStrength)
admin.site.register(LogEntry)
