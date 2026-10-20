from django.contrib import admin
from django.utils.html import format_html

from .models import CoreSkill, Image, LogEntry, Project, SkillCategory, TechnicalStrength


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
    list_display = ("name", "active", "preview_thumbnail", "image_count", "link")
    list_filter = ("active",)
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
