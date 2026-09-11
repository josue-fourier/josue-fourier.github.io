from modeltranslation.translator import TranslationOptions, register

from .models import Project, LogEntry


@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ('description', )

@register(LogEntry)
class LogEntryTranslationOptions(TranslationOptions):
    fields = ('title','content',)
