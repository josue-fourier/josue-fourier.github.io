from django.db import models


class Project(models.Model):
    name = models.CharField(null=False, max_length=100)
    active = models.BooleanField(default=False)
    description = models.CharField(null=False, max_length=200)
    stack = models.CharField(null=False, max_length=100)
    link = models.URLField(null=True, blank=True)

    def __str__ (self):
        return f"Project {self.name}"

class TechnicalStrength(models.Model):
    technology = models.CharField(null=False, max_length=50)

    def __str__ (self):
        return self.technology
