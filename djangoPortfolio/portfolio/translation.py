from modeltranslation.translator import TranslationOptions, register

from .models import Project, LogEntry, SkillCategory, CoreSkill


@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ('description', 'content')

@register(LogEntry)
class LogEntryTranslationOptions(TranslationOptions):
    fields = ('title','content',)

@register(SkillCategory)
class SkillCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(CoreSkill)
class CoreSkillTranslationOptions(TranslationOptions):
    fields = ('name',)
