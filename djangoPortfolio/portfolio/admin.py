from django.contrib import admin
from django.utils.html import format_html

from .models import (
    CoreSkill,
    HackerRankBadge,
    Image,
    LogEntry,
    NodeHeartbeat,
    Project,
    SkillCategory,
    Status,
    TechnicalStrength,
)


class ProjectImageInline(admin.TabularInline):
    model = Image
    fk_name = "project"
    extra = 1
    fields = ("file", "thumbnail_preview", "is_main_preview", "alt_text", "caption", "order")
    readonly_fields = ("thumbnail_preview",)

    def thumbnail_preview(self, obj):
        if obj and obj.file:
            return format_html('<img src="{}" style="max-height: 50px; border-radius: 4px;" />', obj.file.url)
        return "-"

    thumbnail_preview.short_description = "Preview"


class LogImageInline(admin.TabularInline):
    model = Image
    fk_name = "log"
    extra = 1
    fields = ("file", "thumbnail_preview", "alt_text", "caption", "order")
    readonly_fields = ("thumbnail_preview",)

    def thumbnail_preview(self, obj):
        if obj and obj.file:
            return format_html('<img src="{}" style="max-height: 50px; border-radius: 4px;" />', obj.file.url)
        return "-"

    thumbnail_preview.short_description = "Preview"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "status", "order", "preview_thumbnail", "image_count", "link")
    list_editable = ("active", "status", "order")
    list_filter = ("active", "status")
    search_fields = ("name", "description")
    inlines = [ProjectImageInline]

    def preview_thumbnail(self, obj):
        img = obj.preview_image
        if img and img.file:
            return format_html('<img src="{}" style="max-height: 40px; border-radius: 4px;" />', img.file.url)
        return "-"

    preview_thumbnail.short_description = "Main Preview"

    def image_count(self, obj):
        return obj.images.count() if obj and obj.pk else 0

    image_count.short_description = "Images"


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "project", "is_featured", "image_count")
    list_filter = ("is_featured", "date", "project")
    search_fields = ("title", "content")
    inlines = [LogImageInline]

    def image_count(self, obj):
        return obj.images.count() if obj and obj.pk else 0

    image_count.short_description = "Images"


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("id", "thumbnail_preview", "project", "is_main_preview", "log", "order", "created_at")
    list_filter = ("is_main_preview", "created_at", "project", "log")
    search_fields = ("id", "alt_text", "caption", "project__name", "log__title")
    readonly_fields = ("id", "created_at", "thumbnail_preview")

    def thumbnail_preview(self, obj):
        if obj and obj.file:
            return format_html('<img src="{}" style="max-height: 80px; border-radius: 4px;" />', obj.file.url)
        return "-"

    thumbnail_preview.short_description = "Preview"


admin.site.register(TechnicalStrength)
admin.site.register(SkillCategory)
admin.site.register(CoreSkill)


@admin.register(HackerRankBadge)
class HackerRankBadgeAdmin(admin.ModelAdmin):
    list_display = ("badge_name", "category_name", "stars", "total_stars", "level", "solved", "timestamp")
    list_filter = ("badge_name", "category_name", "timestamp")
    search_fields = ("badge_name", "category_name", "badge_type")


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("message", "source", "timestamp")
    list_filter = ("source", "timestamp")
    search_fields = ("message",)


@admin.register(NodeHeartbeat)
class NodeHeartbeatAdmin(admin.ModelAdmin):
    list_display = ("node_name", "status_preview", "is_recent", "timestamp")
    list_filter = ("node_name", "timestamp")
    search_fields = ("node_name", "status")

    def status_preview(self, obj):
        return obj.status[:60] + "..." if len(obj.status) > 60 else obj.status

    status_preview.short_description = "Status Payload"

