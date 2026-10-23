import math
import uuid
from pathlib import Path

from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TechnicalStrength(models.Model):
    technology = models.CharField(null=False, max_length=50, unique=True)

    def __str__ (self):
        return self.technology


class Project(models.Model):
    STATUS_CHOICES = [
        ("production", _("In production")),
        ("development", _("In development")),
        ("academic", _("Academic project")),
        ("personal", _("Personal infrastructure")),
    ]

    name = models.CharField(null=False, max_length=100)
    active = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="development")
    order = models.PositiveIntegerField(default=0, help_text="Lower shows first on the home page")
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
            from django.core.exceptions import ValidationError
            from PIL import Image as PILImage
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
    badge_category = models.CharField(max_length=300, null=True, blank=True)
    badge_type = models.CharField(max_length=100, null=True, blank=True)
    category_name = models.CharField(max_length=300, null=True, blank=True)
    badge_name = models.CharField(max_length=300, null=True, blank=True)
    badge_short_name = models.CharField(max_length=100, null=True, blank=True)
    total_stars = models.PositiveIntegerField(default=0, null=True, blank=True)
    total_points = models.PositiveIntegerField(null=True, blank=True)
    url = models.CharField(max_length=500, null=True, blank=True)
    stars = models.PositiveIntegerField(default=0, null=True, blank=True)
    level = models.PositiveIntegerField(default=1, null=True, blank=True)
    current_points = models.FloatField(default=0.0, null=True, blank=True)
    progress_to_next_star = models.FloatField(default=0.0, null=True, blank=True)
    upcoming_level = models.PositiveIntegerField(null=True, blank=True)
    solved = models.PositiveIntegerField(default=0, null=True, blank=True)
    total_challenges = models.PositiveIntegerField(default=0, null=True, blank=True)
    hacker_rank = models.BigIntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-stars", "badge_name"]
        verbose_name = "HackerRank Badge"
        verbose_name_plural = "HackerRank Badges"

    def __str__(self):
        return f"{self.badge_name or 'Badge'} ({self.stars or 0}/{self.total_stars or 0} stars)"

    def save(self, *args, **kwargs):
        if self.url and not (self.url.startswith("http://") or self.url.startswith("https://")):
            if self.url.startswith("/"):
                self.url = f"https://www.hackerrank.com{self.url}"
            else:
                self.url = f"https://www.hackerrank.com/{self.url}"
        if self.url and len(self.url) > 500:
            self.url = self.url[:500]
        if not self.badge_name:
            self.badge_name = "Unnamed Badge"
        elif len(self.badge_name) > 300:
            self.badge_name = self.badge_name[:300]
        if self.category_name and len(self.category_name) > 300:
            self.category_name = self.category_name[:300]
        if self.badge_category and len(self.badge_category) > 300:
            self.badge_category = self.badge_category[:300]
        if self.badge_type and len(self.badge_type) > 100:
            self.badge_type = self.badge_type[:100]
        if self.badge_short_name and len(self.badge_short_name) > 100:
            self.badge_short_name = self.badge_short_name[:100]

        # Bounds and NaN protection for PostgreSQL integer & float fields
        MAX_INT = 2147483647
        MAX_BIGINT = 9223372036854775807
        for field in ("total_stars", "total_points", "stars", "level", "upcoming_level", "solved", "total_challenges"):
            val = getattr(self, field)
            if val is not None:
                if val < 0:
                    setattr(self, field, 0 if field not in ("level", "upcoming_level") else 1)
                elif val > MAX_INT:
                    setattr(self, field, MAX_INT)

        if self.hacker_rank is not None:
            if self.hacker_rank < 0:
                self.hacker_rank = 0
            elif self.hacker_rank > MAX_BIGINT:
                self.hacker_rank = MAX_BIGINT

        if self.progress_to_next_star is not None:
            if math.isnan(self.progress_to_next_star) or math.isinf(self.progress_to_next_star):
                self.progress_to_next_star = 0.0
            else:
                self.progress_to_next_star = max(0.0, min(1.0, float(self.progress_to_next_star)))

        if self.current_points is not None:
            if math.isnan(self.current_points) or math.isinf(self.current_points) or self.current_points < 0.0:
                self.current_points = 0.0

        super().save(*args, **kwargs)

    @property
    def display_category(self):
        if self.category_name:
            return self.category_name
        if self.badge_type:
            return self.badge_type.replace("-", " ").title()
        if self.badge_category:
            return self.badge_category.replace("HackerBadge::", "")
        return "Skill"

    @property
    def domain_url(self):
        if not self.url:
            return "https://www.hackerrank.com"
        if self.url.startswith("http://") or self.url.startswith("https://"):
            return self.url
        if self.url.startswith("/"):
            return f"https://www.hackerrank.com{self.url}"
        return f"https://www.hackerrank.com/{self.url}"

    @property
    def progress_percentage(self):
        if self.progress_to_next_star is None or math.isnan(self.progress_to_next_star) or math.isinf(self.progress_to_next_star):
            return 0
        return max(0, min(100, int(round(self.progress_to_next_star * 100))))

    @property
    def display_total_stars(self):
        return max(self.total_stars or 0, self.stars or 0)

    @property
    def stars_list(self):
        total = min(20, max(self.total_stars or 0, self.stars or 0))
        earned = min(total, max(0, self.stars or 0))
        return [{"filled": i < earned} for i in range(total)]


class Status(models.Model):
    message = models.CharField(max_length=280)
    source = models.CharField(max_length=50, default="admin", help_text="Source: admin, ntfy, etc.")
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Status"
        verbose_name_plural = "Statuses"

    def __str__(self):
        return f"{self.message} ({self.timestamp:%Y-%m-%d %H:%M})"


class NodeHeartbeat(models.Model):
    node_name = models.CharField(max_length=100, default="raspberry-pi", unique=True)
    status = models.TextField(help_text="Arbitrary telemetry string sent by node")
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Node Heartbeat"
        verbose_name_plural = "Node Heartbeats"

    def __str__(self):
        return f"{self.node_name}: {self.status[:50]} ({self.timestamp:%Y-%m-%d %H:%M})"

    @property
    def is_recent(self):
        import datetime
        return timezone.now() - self.timestamp < datetime.timedelta(minutes=20)



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
