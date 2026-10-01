from django.contrib import admin

from .models import LogEntry, Project, TechnicalStrength, SkillCategory, CoreSkill

admin.site.register(Project)
admin.site.register(TechnicalStrength)
admin.site.register(LogEntry)
admin.site.register(SkillCategory)
admin.site.register(CoreSkill)
