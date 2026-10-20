from pathlib import Path
import uuid

from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver


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

    @property
    def preview_image(self):
        if not self.pk:
            return None
        imgs = list(self.images.all())
        for img in imgs:
            if img.is_main_preview:
                return img
        return imgs[0] if imgs else None


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


class SkillCategory(models.Model):
    name = models.CharField(null=False, blank=False, max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Skill Categories"

    def __str__(self):
        return self.name

class CoreSkill(models.Model):
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(null=False, blank=False, max_length=100)

    class Meta:
        ordering = ["category__order", "name"]
        verbose_name_plural = "Core Skills"

    def __str__(self):
        return self.name


def get_image_upload_path(instance, filename):
    ext = Path(filename).suffix.lower() or ".jpg"
    img_id = getattr(instance, "id", None)
    if not img_id:
        img_id = uuid.uuid4()
        instance.id = img_id
    return f"images/{img_id}{ext}"


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ImageField(upload_to=get_image_upload_path)
    alt_text = models.CharField(max_length=255, blank=True, default="", help_text="Accessibility alt description")
    caption = models.CharField(max_length=255, blank=True, default="", help_text="Optional caption")
    order = models.PositiveIntegerField(default=0, help_text="Ordering sequence")
    created_at = models.DateTimeField(auto_now_add=True)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="images"
    )
    is_main_preview = models.BooleanField(
        default=False,
        help_text="Designate as the main preview image for the project"
    )

    log = models.ForeignKey(
        LogEntry,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="images"
    )

    class Meta:
        ordering = ["order", "created_at"]
        verbose_name = "Image"
        verbose_name_plural = "Images"

    def __str__(self):
        target = f"Project: {self.project.name}" if self.project else (f"Log: {self.log.title}" if self.log else "Unassigned")
        return f"Image {self.id} ({target})"

    def clean(self):
        super().clean()
        if self.file:
            from PIL import Image as PILImage
            from django.core.exceptions import ValidationError
            try:
                if hasattr(self.file, "seek"):
                    self.file.seek(0)
                pil_img = PILImage.open(self.file)
                pil_img.verify()
                if hasattr(self.file, "seek"):
                    self.file.seek(0)
            except Exception as e:
                raise ValidationError({"file": f"Invalid or corrupted image: {e}"})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        if self.is_main_preview and self.project_id:
            Image.objects.filter(project_id=self.project_id, is_main_preview=True).exclude(pk=self.pk).update(is_main_preview=False)

class HackerRankBadge(models.Model): 
    # Endpoint https://www.hackerrank.com/rest/hackers/xmenmagnet/badges
    # The data of all the objects with the following shape, is an array named models.
    badge_category = models.CharField(max_length=300)
    badge_type = models.CharField(max_length=50)
    category_name = models.CharField(max_length=300)
    badge_name = models.CharField(max_length=300)
    badge_short_name = models.CharField(max_length=50)
    total_stars = models.PositiveIntegerField()
    total_points = models.PositiveIntegerField()
    url = models.URLField()
    stars = models.PositiveIntegerField()
    level = models.PositiveIntegerField()
    current_points = models.PositiveIntegerField()
    progress_to_next_star = models.FloatField()
    upcoming_level = models.PositiveIntegerField()
    solved = models.PositiveIntegerField()
    total_challenges = models.PositiveIntegerField()
    hacker_rank = models.PositiveIntegerField()
    


@receiver(post_delete, sender=Image)
def delete_image_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        try:
            instance.file.delete(save=False)
        except Exception:
            pass


@receiver(pre_save, sender=Image)
def delete_old_image_file_on_change(sender, instance, **kwargs):
    if getattr(instance, "_state", None) and instance._state.adding:
        return
    if not instance.pk:
        return
    try:
        old_obj = sender.objects.get(pk=instance.pk)
        if old_obj.file and old_obj.file != instance.file:
            old_obj.file.delete(save=False)
    except sender.DoesNotExist:
        pass
    except Exception:
        pass

