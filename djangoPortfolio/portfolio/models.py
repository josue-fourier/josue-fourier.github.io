import uuid

from django.db import models


class TechnicalStrength(models.Model):
    technology = models.CharField(null=False, max_length=50, unique=True)

    def __str__ (self):
        return self.technology


class Project(models.Model):
    name = models.CharField(null=False, max_length=100)
    active = models.BooleanField(default=False)
    description = models.TextField(null=False)
    content = models.TextField(null=True, blank=True, help_text="Markdown content for the project case study")
    stack = models.ManyToManyField(TechnicalStrength, related_name="projects", related_query_name="project")
    link = models.URLField(null=True, blank=True)

    def __str__ (self):
        return f"Project {self.name}"


class LogEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(null=False, blank=False, max_length=200)
    date = models.DateTimeField(auto_now_add=True, null=False)
    content = models.TextField(null=False, blank=False)
    is_featured = models.BooleanField(default=False)

    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    stack = models.ManyToManyField(TechnicalStrength, related_name="logs", related_query_name="log", blank=True)

    class Meta:
        get_latest_by="-date"
        ordering = ["-date",]
        verbose_name_plural = "Log entries"

    def __str__(self):
        return f"Log {self.title}"
