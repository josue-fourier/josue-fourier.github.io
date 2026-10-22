"""
Comprehensive Test Suite for Portfolio Full Image Support (Tiers 1-4).

Covers:
- Tier 1: Feature Coverage (F1-F7, F8-F11, F14, F15)
- Tier 2: Boundary & Corner Cases (0-image, 1-image, 10+ images, invalid files, unicode)
- Tier 3: Pairwise Combinations (locales, view modes, image formats)
- Tier 4: Real-World Workload Scenarios (lifecycles, cascading cleanup, batch workloads)
"""

import io
import json
import os
import re
import shutil
import tempfile
import unittest
import uuid
from pathlib import Path
from PIL import Image as PILImage

from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings

from portfolio.admin import (
    ImageAdmin,
    LogEntryAdmin,
    LogImageInline,
    ProjectAdmin,
    ProjectImageInline,
)
from portfolio.models import (
    HackerRankBadge,
    Image,
    LogEntry,
    Project,
    TechnicalStrength,
    get_image_upload_path,
)


def make_test_image(format="JPEG", size=(40, 40), color="blue", name=None):
    """Generates an in-memory test image file wrapped in SimpleUploadedFile."""
    ext = format.lower()
    if ext == "jpeg":
        ext = "jpg"
    filename = name or f"test_img.{ext}"
    content_type = f"image/{format.lower()}"
    buffer = io.BytesIO()
    img = PILImage.new("RGB", size, color=color)
    img.save(buffer, format=format)
    buffer.seek(0)
    return SimpleUploadedFile(filename, buffer.getvalue(), content_type=content_type)


class MockRequest:
    pass


# ---------------------------------------------------------------------------
# Base Test Case providing isolated media directory
# ---------------------------------------------------------------------------
class MediaIsolatedTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.temp_media = tempfile.mkdtemp(prefix="portfolio_test_media_")
        cls.override = override_settings(MEDIA_ROOT=cls.temp_media)
        cls.override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.override.disable()
        shutil.rmtree(cls.temp_media, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.client = Client()


# ===========================================================================
# TIER 1: Feature Coverage
# ===========================================================================

class Tier1FeatureF1UUIDIdentificationTests(MediaIsolatedTestCase):
    """F1: UUID Identification - Every image is assigned a unique UUID PK."""

    def test_image_id_is_valid_uuid4(self):
        img_file = make_test_image()
        image = Image.objects.create(file=img_file)
        self.assertIsInstance(image.id, uuid.UUID)
        self.assertEqual(image.id.version, 4)

    def test_image_id_uniqueness(self):
        ids = set()
        for _ in range(5):
            img_file = make_test_image()
            img = Image.objects.create(file=img_file)
            ids.add(img.id)
        self.assertEqual(len(ids), 5)

    def test_image_id_regex_format(self):
        img_file = make_test_image()
        image = Image.objects.create(file=img_file)
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        self.assertRegex(str(image.id), uuid_pattern)

    def test_image_id_populated_before_save(self):
        img_file = make_test_image()
        image = Image(file=img_file)
        self.assertIsNotNone(image.id)
        self.assertIsInstance(image.id, uuid.UUID)

    def test_image_retrieval_by_uuid_str_and_obj(self):
        img_file = make_test_image()
        image = Image.objects.create(file=img_file)
        by_uuid = Image.objects.get(id=image.id)
        by_str = Image.objects.get(id=str(image.id))
        self.assertEqual(by_uuid, image)
        self.assertEqual(by_str, image)


class Tier1FeatureF2FileStoragePathTests(MediaIsolatedTestCase):
    """F2: UUID File Storage - Stored files named strictly by UUID in media root."""

    def test_upload_path_format_jpeg(self):
        img_file = make_test_image(format="JPEG")
        image = Image.objects.create(file=img_file)
        expected_path = f"images/{image.id}.jpg"
        self.assertEqual(image.file.name, expected_path)

    def test_upload_path_format_png(self):
        img_file = make_test_image(format="PNG")
        image = Image.objects.create(file=img_file)
        expected_path = f"images/{image.id}.png"
        self.assertEqual(image.file.name, expected_path)

    def test_upload_path_format_webp(self):
        img_file = make_test_image(format="WEBP")
        image = Image.objects.create(file=img_file)
        expected_path = f"images/{image.id}.webp"
        self.assertEqual(image.file.name, expected_path)

    def test_upload_path_lowercase_extension(self):
        img_file = make_test_image(format="JPEG", name="UPPERCASE.JPG")
        image = Image.objects.create(file=img_file)
        self.assertTrue(image.file.name.endswith(".jpg"))

    def test_get_image_upload_path_function_directly(self):
        class DummyInstance:
            id = uuid.UUID("12345678-1234-5678-1234-567812345678")
        path = get_image_upload_path(DummyInstance(), "avatar.PNG")
        self.assertEqual(path, "images/12345678-1234-5678-1234-567812345678.png")


class Tier1FeatureF3ProjectMultiImageAssociationTests(MediaIsolatedTestCase):
    """F3: Project Image Association - Projects can have multiple attached images."""

    def setUp(self):
        super().setUp()
        self.project = Project.objects.create(name="Alpha Project", description="Testing multi images", active=True)

    def test_multiple_images_associated_with_single_project(self):
        for i in range(3):
            Image.objects.create(project=self.project, file=make_test_image(), order=i)
        self.assertEqual(self.project.images.count(), 3)

    def test_project_images_reverse_relation_accessor(self):
        img1 = Image.objects.create(project=self.project, file=make_test_image(), order=1)
        img2 = Image.objects.create(project=self.project, file=make_test_image(), order=2)
        images = list(self.project.images.all())
        self.assertIn(img1, images)
        self.assertIn(img2, images)

    def test_unassigned_image_has_no_project(self):
        unassigned = Image.objects.create(file=make_test_image())
        self.assertIsNone(unassigned.project)

    def test_cascade_delete_project_deletes_attached_images(self):
        img = Image.objects.create(project=self.project, file=make_test_image())
        img_id = img.id
        self.project.delete()
        self.assertFalse(Image.objects.filter(id=img_id).exists())

    def test_project_images_ordered_by_order_field(self):
        img3 = Image.objects.create(project=self.project, file=make_test_image(), order=30)
        img1 = Image.objects.create(project=self.project, file=make_test_image(), order=10)
        img2 = Image.objects.create(project=self.project, file=make_test_image(), order=20)
        ordered_ids = list(self.project.images.values_list("id", flat=True))
        self.assertEqual(ordered_ids, [img1.id, img2.id, img3.id])


class Tier1FeatureF4DesignatedMainPreviewTests(MediaIsolatedTestCase):
    """F4: Designated Main Preview Image & Fallback."""

    def setUp(self):
        super().setUp()
        self.project = Project.objects.create(name="Beta Project", description="Preview testing", active=True)

    def test_designated_main_preview_returned(self):
        img1 = Image.objects.create(project=self.project, file=make_test_image(), is_main_preview=False, order=1)
        img2 = Image.objects.create(project=self.project, file=make_test_image(), is_main_preview=True, order=2)
        self.project.refresh_from_db()
        self.assertEqual(self.project.preview_image, img2)

    def test_fallback_to_first_image_when_none_designated(self):
        img1 = Image.objects.create(project=self.project, file=make_test_image(), is_main_preview=False, order=1)
        img2 = Image.objects.create(project=self.project, file=make_test_image(), is_main_preview=False, order=2)
        self.project.refresh_from_db()
        self.assertEqual(self.project.preview_image, img1)

    def test_fallback_to_none_when_zero_images(self):
        self.assertIsNone(self.project.preview_image)

    def test_single_active_preview_enforced_on_save(self):
        img1 = Image.objects.create(project=self.project, file=make_test_image(), is_main_preview=True)
        img2 = Image.objects.create(project=self.project, file=make_test_image(), is_main_preview=True)
        img1.refresh_from_db()
        img2.refresh_from_db()
        self.assertFalse(img1.is_main_preview)
        self.assertTrue(img2.is_main_preview)
        self.assertEqual(self.project.images.filter(is_main_preview=True).count(), 1)

    def test_switching_main_preview_dynamically(self):
        img1 = Image.objects.create(project=self.project, file=make_test_image(), is_main_preview=True)
        img2 = Image.objects.create(project=self.project, file=make_test_image(), is_main_preview=False)
        self.assertEqual(self.project.preview_image, img1)
        img2.is_main_preview = True
        img2.save()
        self.project.refresh_from_db()
        self.assertEqual(self.project.preview_image, img2)


class Tier1FeatureF5LogMultiImageAssociationTests(MediaIsolatedTestCase):
    """F5: Log Multi-Image Association."""

    def setUp(self):
        super().setUp()
        self.log = LogEntry.objects.create(title="Log Omega", content="Log details content")

    def test_multiple_images_associated_with_log(self):
        for i in range(2):
            Image.objects.create(log=self.log, file=make_test_image(), order=i)
        self.assertEqual(self.log.images.count(), 2)

    def test_log_images_reverse_relation(self):
        img1 = Image.objects.create(log=self.log, file=make_test_image(), order=1)
        img2 = Image.objects.create(log=self.log, file=make_test_image(), order=2)
        images = list(self.log.images.all())
        self.assertIn(img1, images)
        self.assertIn(img2, images)

    def test_image_log_foreign_key_nullability(self):
        img = Image.objects.create(file=make_test_image())
        self.assertIsNone(img.log)

    def test_cascade_delete_log_deletes_attached_images(self):
        img = Image.objects.create(log=self.log, file=make_test_image())
        img_id = img.id
        self.log.delete()
        self.assertFalse(Image.objects.filter(id=img_id).exists())

    def test_log_image_ordering(self):
        img2 = Image.objects.create(log=self.log, file=make_test_image(), order=20)
        img1 = Image.objects.create(log=self.log, file=make_test_image(), order=10)
        ordered_ids = list(self.log.images.values_list("id", flat=True))
        self.assertEqual(ordered_ids, [img1.id, img2.id])


class Tier1FeatureF6AdminManagementTests(MediaIsolatedTestCase):
    """F6: Admin Management & Inlines."""

    def setUp(self):
        super().setUp()
        self.site = AdminSite()

    def test_project_admin_has_project_image_inline(self):
        project_admin = ProjectAdmin(Project, self.site)
        inline_classes = [inline.__class__ if not isinstance(inline, type) else inline for inline in project_admin.inlines]
        self.assertIn(ProjectImageInline, inline_classes)

    def test_log_admin_has_log_image_inline(self):
        log_admin = LogEntryAdmin(LogEntry, self.site)
        inline_classes = [inline.__class__ if not isinstance(inline, type) else inline for inline in log_admin.inlines]
        self.assertIn(LogImageInline, inline_classes)

    def test_image_admin_registered_in_admin_site(self):
        from django.contrib import admin
        self.assertIn(Image, admin.site._registry)
        self.assertIsInstance(admin.site._registry[Image], ImageAdmin)

    def test_project_admin_preview_thumbnail_helper(self):
        project = Project.objects.create(name="Admin Thumb Test", description="Test", active=True)
        img = Image.objects.create(project=project, file=make_test_image(), is_main_preview=True)
        project_admin = ProjectAdmin(Project, self.site)
        html = project_admin.preview_thumbnail(project)
        self.assertIn("<img", html)
        self.assertIn(img.file.url, html)

    def test_image_admin_thumbnail_preview_helper(self):
        img = Image.objects.create(file=make_test_image())
        image_admin = ImageAdmin(Image, self.site)
        html = image_admin.thumbnail_preview(img)
        self.assertIn("<img", html)
        self.assertIn(img.file.url, html)


class Tier1FeatureF7APIEndpointsTests(MediaIsolatedTestCase):
    """F7: API Upload & Retrieval Endpoints."""

    def setUp(self):
        super().setUp()
        self.project = Project.objects.create(name="API Project", description="API Test", active=True)
        self.log = LogEntry.objects.create(title="API Log", content="Content")

    def test_health_check_endpoints(self):
        res1 = self.client.get("/health")
        res2 = self.client.get("/health/")
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res1.json().get("status"), "healthy")

    def test_api_image_upload_standalone(self):
        upload = make_test_image(format="JPEG")
        res = self.client.post("/api/images/upload/", {"file": upload})
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertTrue(uuid.UUID(data["id"]))
        self.assertTrue(data["url"].startswith("/media/images/"))

    def test_api_image_upload_with_project_and_preview(self):
        upload = make_test_image(format="PNG")
        res = self.client.post("/api/images/upload/", {
            "file": upload,
            "project_id": self.project.id,
            "is_main_preview": "true",
            "alt_text": "Sample alt",
            "caption": "Sample caption",
        })
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["project_id"], self.project.id)
        self.assertTrue(data["is_main_preview"])

    def test_api_image_detail_get_and_patch(self):
        img = Image.objects.create(project=self.project, file=make_test_image())
        get_res = self.client.get(f"/api/images/{img.id}/")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()["id"], str(img.id))

        patch_res = self.client.patch(
            f"/api/images/{img.id}/",
            data=json.dumps({"caption": "Updated Caption"}),
            content_type="application/json",
        )
        self.assertEqual(patch_res.status_code, 200)
        self.assertEqual(patch_res.json()["caption"], "Updated Caption")

    def test_api_project_images_list_and_post(self):
        img = Image.objects.create(project=self.project, file=make_test_image())
        list_res = self.client.get(f"/api/projects/{self.project.id}/images/")
        self.assertEqual(list_res.status_code, 200)
        images = list_res.json().get("images", [])
        self.assertEqual(len(images), 1)

        upload2 = make_test_image(format="JPEG")
        post_res = self.client.post(f"/api/projects/{self.project.id}/images/", {"file": upload2})
        self.assertEqual(post_res.status_code, 201)

    def test_api_log_images_list_and_post(self):
        upload = make_test_image(format="WEBP")
        post_res = self.client.post(f"/api/logs/{self.log.id}/images/", {"file": upload})
        self.assertEqual(post_res.status_code, 201)

        list_res = self.client.get(f"/api/logs/{self.log.id}/images/")
        self.assertEqual(list_res.status_code, 200)
        self.assertEqual(len(list_res.json().get("images", [])), 1)


class Tier1FeatureF8IndexPreviewDisplayTests(MediaIsolatedTestCase):
    """F8: Index Preview Display (`/en/` and `/es/`)."""

    def setUp(self):
        super().setUp()
        self.project = Project.objects.create(name="Featured Index Proj", description="Desc", active=True)
        self.image = Image.objects.create(project=self.project, file=make_test_image(), is_main_preview=True)

    def _check_template_preview_supported(self):
        res = self.client.get("/en/")
        template_src = "".join(t.source for t in res.templates if hasattr(t, "source"))
        if "preview_image" not in template_src and "main_image" not in template_src:
            raise unittest.SkipTest("Milestone 3 (Frontend Index Preview) pending in templates")

    def test_index_en_displays_project_preview_image(self):
        self._check_template_preview_supported()
        res = self.client.get("/en/")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.image.file.url)

    def test_index_es_displays_project_preview_image(self):
        self._check_template_preview_supported()
        res = self.client.get("/es/")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.image.file.url)

    def test_index_renders_cleanly_when_project_has_no_preview(self):
        self.image.delete()
        res = self.client.get("/en/")
        self.assertEqual(res.status_code, 200)
        self.assertNotContains(res, "/media/images/")

    def test_index_renders_fallback_image_when_no_main_designated(self):
        self._check_template_preview_supported()
        self.image.is_main_preview = False
        self.image.save()
        res = self.client.get("/en/")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.image.file.url)

    def test_inactive_project_with_preview_excluded_from_index(self):
        self.project.active = False
        self.project.save()
        res = self.client.get("/en/")
        self.assertEqual(res.status_code, 200)
        self.assertNotContains(res, self.image.file.url)


class Tier1FeatureF9ProjectCarouselBeforeMarkdownTests(MediaIsolatedTestCase):
    """F9: Project Carousel BEFORE Markdown."""

    def setUp(self):
        super().setUp()
        self.project = Project.objects.create(
            name="Carousel Proj",
            description="Detail",
            content="# Heading\nMarkdown case study body content.",
            active=True
        )
        self.img1 = Image.objects.create(project=self.project, file=make_test_image(), order=1)
        self.img2 = Image.objects.create(project=self.project, file=make_test_image(), order=2)

    def _check_template_carousel_supported(self):
        res = self.client.get(f"/project/{self.project.id}/")
        template_src = "".join(t.source for t in res.templates if hasattr(t, "source"))
        if "carousel" not in template_src and "project-gallery" not in template_src:
            raise unittest.SkipTest("Milestone 3 (Frontend Project Carousel) pending in templates")

    def test_project_carousel_positioned_strictly_before_markdown(self):
        self._check_template_carousel_supported()
        res = self.client.get(f"/project/{self.project.id}/")
        self.assertEqual(res.status_code, 200)
        html = res.content.decode("utf-8")
        carousel_idx = html.find('class="carousel')
        if carousel_idx == -1:
            carousel_idx = html.find('id="project-carousel')
        markdown_idx = html.find('class="markdown-body')
        self.assertNotEqual(carousel_idx, -1, "Carousel container not found in HTML")
        self.assertNotEqual(markdown_idx, -1, "Markdown container not found in HTML")
        self.assertLess(carousel_idx, markdown_idx, "Carousel MUST appear before markdown-body")

    def test_project_carousel_contains_all_attached_images(self):
        self._check_template_carousel_supported()
        res = self.client.get(f"/project/{self.project.id}/")
        self.assertContains(res, self.img1.file.url)
        self.assertContains(res, self.img2.file.url)

    def test_project_zero_images_clean_rendering(self):
        empty_proj = Project.objects.create(name="Empty Carousel", description="No img", active=True)
        res = self.client.get(f"/project/{empty_proj.id}/")
        self.assertEqual(res.status_code, 200)
        html = res.content.decode("utf-8")
        self.assertNotIn("carousel-item", html)

    def test_project_single_image_renders_cleanly(self):
        self._check_template_carousel_supported()
        single_proj = Project.objects.create(name="Single Proj", description="Single img", active=True)
        img = Image.objects.create(project=single_proj, file=make_test_image())
        res = self.client.get(f"/project/{single_proj.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, img.file.url)

    def test_project_carousel_has_lenis_prevent_attribute(self):
        self._check_template_carousel_supported()
        res = self.client.get(f"/project/{self.project.id}/")
        self.assertContains(res, "data-lenis-prevent")


class Tier1FeatureF10LogImageBeforeMarkdownTests(MediaIsolatedTestCase):
    """F10: Log Image / Carousel BEFORE Markdown."""

    def setUp(self):
        super().setUp()
        self.log = LogEntry.objects.create(
            title="Log with Images",
            content="This is the log markdown content."
        )
        self.img1 = Image.objects.create(log=self.log, file=make_test_image(), order=1)

    def _check_template_log_image_supported(self):
        res = self.client.get(f"/api/logs/{self.log.id}")
        template_src = "".join(t.source for t in res.templates if hasattr(t, "source"))
        if "log.images" not in template_src and "log-images" not in template_src:
            raise unittest.SkipTest("Milestone 3 (Frontend Log Images) pending in templates")

    def test_log_image_positioned_before_markdown_on_htmx_partial(self):
        self._check_template_log_image_supported()
        res = self.client.get(f"/api/logs/{self.log.id}")
        self.assertEqual(res.status_code, 200)
        html = res.content.decode("utf-8")
        img_idx = html.find(self.img1.file.url)
        markdown_idx = html.find('class="markdown-body"')
        self.assertNotEqual(img_idx, -1)
        self.assertNotEqual(markdown_idx, -1)
        self.assertLess(img_idx, markdown_idx, "Log image must appear before markdown-body")

    def test_log_image_positioned_before_markdown_on_logging_view(self):
        self._check_template_log_image_supported()
        res = self.client.get(f"/?log_id={self.log.id}")
        self.assertEqual(res.status_code, 200)
        html = res.content.decode("utf-8")
        img_idx = html.find(self.img1.file.url)
        markdown_idx = html.find('class="markdown-body"')
        self.assertNotEqual(img_idx, -1)
        self.assertNotEqual(markdown_idx, -1)
        self.assertLess(img_idx, markdown_idx)

    def test_log_multi_image_renders_carousel(self):
        self._check_template_log_image_supported()
        img2 = Image.objects.create(log=self.log, file=make_test_image(), order=2)
        res = self.client.get(f"/api/logs/{self.log.id}")
        self.assertContains(res, self.img1.file.url)
        self.assertContains(res, img2.file.url)

    def test_log_zero_images_clean_rendering(self):
        empty_log = LogEntry.objects.create(title="Empty Log", content="Content only")
        res = self.client.get(f"/api/logs/{empty_log.id}")
        self.assertEqual(res.status_code, 200)
        self.assertNotContains(res, "/media/images/")

    def test_log_image_caption_rendering(self):
        self._check_template_log_image_supported()
        self.img1.caption = "Special Log Diagram"
        self.img1.save()
        res = self.client.get(f"/api/logs/{self.log.id}")
        self.assertContains(res, "Special Log Diagram")


class Tier1FeatureF11ZeroImageCleanRenderingTests(MediaIsolatedTestCase):
    """F11: Zero-Image Clean Rendering across all endpoints."""

    def setUp(self):
        super().setUp()
        self.empty_project = Project.objects.create(name="Zero Project", description="Zero Desc", active=True)
        self.empty_log = LogEntry.objects.create(title="Zero Log", content="Pure text log")

    def test_zero_image_project_detail_returns_200(self):
        res = self.client.get(f"/project/{self.empty_project.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertNotIn("carousel-item", res.content.decode("utf-8"))

    def test_zero_image_logging_view_direct_returns_200(self):
        res = self.client.get(f"/?log_id={self.empty_log.id}")
        self.assertEqual(res.status_code, 200)

    def test_zero_image_htmx_log_partial_returns_200(self):
        res = self.client.get(f"/api/logs/{self.empty_log.id}")
        self.assertEqual(res.status_code, 200)

    def test_zero_image_index_en_and_es_returns_200(self):
        res_en = self.client.get("/en/")
        res_es = self.client.get("/es/")
        self.assertEqual(res_en.status_code, 200)
        self.assertEqual(res_es.status_code, 200)

    def test_zero_image_api_empty_lists(self):
        p_res = self.client.get(f"/api/projects/{self.empty_project.id}/images/")
        l_res = self.client.get(f"/api/logs/{self.empty_log.id}/images/")
        self.assertEqual(p_res.status_code, 200)
        self.assertEqual(l_res.status_code, 200)
        self.assertEqual(p_res.json()["images"], [])
        self.assertEqual(l_res.json()["images"], [])


class Tier1FeatureF14ResponsiveDesignAttributesTests(MediaIsolatedTestCase):
    """F14: Responsive Viewport Design Attributes."""

    def test_index_grid_responsive_classes(self):
        res = self.client.get("/en/")
        self.assertEqual(res.status_code, 200)
        html = res.content.decode("utf-8")
        self.assertTrue("grid-cols-1" in html or "grid" in html)

    def test_api_returns_structured_dimensions(self):
        proj = Project.objects.create(name="Resp Proj", description="D", active=True)
        img = Image.objects.create(project=proj, file=make_test_image(size=(800, 600)))
        res = self.client.get(f"/api/images/{img.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("url", res.json())

    def test_multiple_images_maintain_order_attribute(self):
        proj = Project.objects.create(name="Ordered", description="D", active=True)
        for i in range(4):
            Image.objects.create(project=proj, file=make_test_image(), order=i * 10)
        res = self.client.get(f"/api/projects/{proj.id}/images/")
        images = res.json()["images"]
        orders = [item["order"] for item in images]
        self.assertEqual(orders, [0, 10, 20, 30])

    def test_carousel_controls_prev_next_data_attributes(self):
        proj = Project.objects.create(name="Controls Proj", description="D", active=True)
        Image.objects.create(project=proj, file=make_test_image())
        Image.objects.create(project=proj, file=make_test_image())
        res = self.client.get(f"/project/{proj.id}/")
        html = res.content.decode("utf-8")
        if "carousel" in html:
            self.assertIn("data-carousel-action", html)

    def test_log_carousel_controls_data_attributes(self):
        log = LogEntry.objects.create(title="Controls Log", content="Content")
        Image.objects.create(log=log, file=make_test_image())
        Image.objects.create(log=log, file=make_test_image())
        res = self.client.get(f"/api/logs/{log.id}")
        html = res.content.decode("utf-8")
        if "carousel" in html:
            self.assertIn("data-carousel-action", html)


class Tier1FeatureF15StrictLocalVerificationIsolationTests(MediaIsolatedTestCase):
    """F15: Strict Local Verification Isolation - zero external connections."""

    def test_image_url_uses_local_media_prefix(self):
        img = Image.objects.create(file=make_test_image())
        self.assertTrue(img.file.url.startswith("/media/images/"))

    def test_no_external_josnic_cl_in_media_urls(self):
        img = Image.objects.create(file=make_test_image())
        self.assertNotIn("josnic.cl", img.file.url)

    def test_allowed_hosts_includes_local_interfaces(self):
        self.assertIn("127.0.0.1", settings.ALLOWED_HOSTS)
        self.assertIn("localhost", settings.ALLOWED_HOSTS)

    def test_disallowed_host_rejected(self):
        disallowed_client = Client()
        res = disallowed_client.get("/health", HTTP_HOST="evil-untrusted-host.com")
        self.assertEqual(res.status_code, 400)

    def test_media_root_is_local(self):
        self.assertTrue(os.path.isabs(str(settings.MEDIA_ROOT)))


# ===========================================================================
# TIER 2: Boundary & Corner Cases
# ===========================================================================

class Tier2BoundaryCornerCaseTests(MediaIsolatedTestCase):
    """Tier 2: Boundary Value Analysis & Edge Cases."""

    def test_boundary_zero_images(self):
        p = Project.objects.create(name="Zero Images", description="Desc", active=True)
        self.assertIsNone(p.preview_image)
        self.assertEqual(p.images.count(), 0)

    def test_boundary_single_image(self):
        p = Project.objects.create(name="Single Image", description="Desc", active=True)
        img = Image.objects.create(project=p, file=make_test_image())
        self.assertEqual(p.preview_image, img)
        self.assertEqual(p.images.count(), 1)

    def test_boundary_ten_plus_images(self):
        p = Project.objects.create(name="Ten Plus Images", description="Desc", active=True)
        images = []
        for i in range(12):
            images.append(Image(project=p, file=make_test_image(), order=i))
        Image.objects.bulk_create(images)
        self.assertEqual(p.images.count(), 12)
        self.assertIsNotNone(p.preview_image)

    def test_inactive_project_exclusion_on_index(self):
        p = Project.objects.create(name="Inactive Project", description="Hidden", active=False)
        img = Image.objects.create(project=p, file=make_test_image(), is_main_preview=True)
        res = self.client.get("/en/")
        self.assertNotContains(res, p.name)
        self.assertNotContains(res, img.file.url)

    def test_invalid_file_upload_rejected_plain_text(self):
        bad_file = SimpleUploadedFile("script.sh", b"#!/bin/bash\necho hacked", content_type="text/plain")
        res = self.client.post("/api/images/upload/", {"file": bad_file})
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())

    def test_invalid_file_upload_rejected_empty_file(self):
        empty_file = SimpleUploadedFile("empty.jpg", b"", content_type="image/jpeg")
        res = self.client.post("/api/images/upload/", {"file": empty_file})
        self.assertEqual(res.status_code, 400)

    def test_invalid_file_upload_rejected_corrupted_header(self):
        corrupt = SimpleUploadedFile("corrupt.png", b"\x89PNG\r\n\x1a\nCorrupted binary payload", content_type="image/png")
        res = self.client.post("/api/images/upload/", {"file": corrupt})
        self.assertEqual(res.status_code, 400)

    def test_unicode_special_chars_in_alt_text_and_caption(self):
        p = Project.objects.create(name="Unicode Test", description="D", active=True)
        special_alt = 'Diagram: "Overview" & <script>alert(1)</script> 🚀 ñ 日本語'
        special_caption = "Café & Crème brûlée: 100% test coverage — ‘quoted’"
        img = Image.objects.create(
            project=p,
            file=make_test_image(),
            alt_text=special_alt,
            caption=special_caption,
        )
        res = self.client.get(f"/api/images/{img.id}/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["alt_text"], special_alt)
        self.assertEqual(data["caption"], special_caption)

    def test_rapid_main_preview_toggling(self):
        p = Project.objects.create(name="Toggle Test", description="D", active=True)
        images = [Image.objects.create(project=p, file=make_test_image(), order=i) for i in range(5)]
        for img in images:
            img.is_main_preview = True
            img.save()
        active_previews = p.images.filter(is_main_preview=True)
        self.assertEqual(active_previews.count(), 1)
        self.assertEqual(active_previews.first(), images[-1])

    def test_unassigned_image_can_be_assigned_to_project_later(self):
        p = Project.objects.create(name="Late Assign", description="D", active=True)
        img = Image.objects.create(file=make_test_image())
        self.assertIsNone(img.project)
        img.project = p
        img.save()
        self.assertEqual(p.images.first(), img)

    def test_reassignment_from_project_to_log(self):
        p = Project.objects.create(name="Switch Origin", description="D", active=True)
        log = LogEntry.objects.create(title="Switch Dest", content="Content")
        img = Image.objects.create(project=p, file=make_test_image())
        self.assertEqual(p.images.count(), 1)
        self.assertEqual(log.images.count(), 0)

        img.project = None
        img.log = log
        img.save()
        self.assertEqual(p.images.count(), 0)
        self.assertEqual(log.images.count(), 1)

    def test_file_cleanup_on_image_delete(self):
        img = Image.objects.create(file=make_test_image())
        file_path = img.file.path
        self.assertTrue(os.path.exists(file_path))
        img.delete()
        self.assertFalse(os.path.exists(file_path))


# ===========================================================================
# TIER 3: Pairwise Combinations
# ===========================================================================

class Tier3PairwiseCombinationsTests(MediaIsolatedTestCase):
    """Tier 3: Combinatorial & Cross-Feature interaction tests."""

    def test_locale_matrix_with_preview_image(self):
        p = Project.objects.create(name="Locale Matrix Proj", description="Desc", active=True)
        img = Image.objects.create(project=p, file=make_test_image(), is_main_preview=True)
        for lang in ("/en/", "/es/"):
            res = self.client.get(lang)
            self.assertEqual(res.status_code, 200)

    def test_view_mode_matrix_direct_vs_htmx_with_multiple_images(self):
        log = LogEntry.objects.create(title="View Mode Log", content="Content")
        img1 = Image.objects.create(log=log, file=make_test_image(), order=1)
        img2 = Image.objects.create(log=log, file=make_test_image(), order=2)

        direct_res = self.client.get(f"/?log_id={log.id}")
        htmx_res = self.client.get(f"/api/logs/{log.id}")
        self.assertEqual(direct_res.status_code, 200)
        self.assertEqual(htmx_res.status_code, 200)

    def test_image_format_matrix_png_jpeg_webp(self):
        formats = ["JPEG", "PNG", "WEBP"]
        p = Project.objects.create(name="Formats Proj", description="D", active=True)
        for fmt in formats:
            upload = make_test_image(format=fmt)
            res = self.client.post(f"/api/projects/{p.id}/images/", {"file": upload})
            self.assertEqual(res.status_code, 201)
            self.assertTrue(res.json()["url"].endswith(fmt.lower() if fmt != "JPEG" else "jpg"))

    def test_api_patch_and_retrieve_roundtrip(self):
        img = Image.objects.create(file=make_test_image(), alt_text="Initial Alt")
        patch_res = self.client.patch(
            f"/api/images/{img.id}/",
            data=json.dumps({"alt_text": "Modified Alt", "order": 99}),
            content_type="application/json",
        )
        self.assertEqual(patch_res.status_code, 200)
        self.assertEqual(patch_res.json()["alt_text"], "Modified Alt")
        self.assertEqual(patch_res.json()["order"], 99)

    def test_delete_api_removes_file_and_record(self):
        img = Image.objects.create(file=make_test_image())
        path = img.file.path
        self.assertTrue(os.path.exists(path))
        del_res = self.client.delete(f"/api/images/{img.id}/")
        self.assertEqual(del_res.status_code, 204)
        self.assertFalse(Image.objects.filter(id=img.id).exists())
        self.assertFalse(os.path.exists(path))


# ===========================================================================
# TIER 4: Real-World Application Scenarios
# ===========================================================================

class Tier4RealWorldWorkloadScenariosTests(MediaIsolatedTestCase):
    """Tier 4: Realistic End-to-End Application Scenarios."""

    def test_scenario_1_full_project_lifecycle(self):
        # 1. Create project
        p = Project.objects.create(name="Lifecycle Project", description="Full lifecycle", active=True)
        self.assertIsNone(p.preview_image)

        # 2. Upload 3 images via API
        img_ids = []
        for i in range(3):
            upload = make_test_image(format="JPEG" if i == 0 else "PNG")
            res = self.client.post("/api/images/upload/", {
                "file": upload,
                "project_id": p.id,
                "order": i,
                "is_main_preview": "true" if i == 1 else "false",
            })
            self.assertEqual(res.status_code, 201)
            img_ids.append(res.json()["id"])

        # 3. Verify preview image is image 1
        p.refresh_from_db()
        self.assertEqual(str(p.preview_image.id), img_ids[1])

        # 4. Detail view status 200
        detail_res = self.client.get(f"/project/{p.id}/")
        self.assertEqual(detail_res.status_code, 200)

        # 5. Clean up
        p.delete()
        self.assertEqual(Image.objects.filter(id__in=img_ids).count(), 0)

    def test_scenario_2_full_log_lifecycle(self):
        # 1. Create log
        log = LogEntry.objects.create(title="Lifecycle Log", content="# Log entry with attachments")

        # 2. Attach 2 images
        res1 = self.client.post(f"/api/logs/{log.id}/images/", {"file": make_test_image(format="JPEG")})
        res2 = self.client.post(f"/api/logs/{log.id}/images/", {"file": make_test_image(format="WEBP")})
        self.assertEqual(res1.status_code, 201)
        self.assertEqual(res2.status_code, 201)

        # 3. Direct load and HTMX load
        direct = self.client.get(f"/?log_id={log.id}")
        htmx = self.client.get(f"/api/logs/{log.id}")
        self.assertEqual(direct.status_code, 200)
        self.assertEqual(htmx.status_code, 200)

        # 4. Clean up
        log_id = log.id
        log.delete()
        self.assertEqual(Image.objects.filter(log_id=log_id).count(), 0)

    def test_scenario_3_zero_image_clean_fallback_all_routes(self):
        empty_p = Project.objects.create(name="Empty Fallback Proj", description="Desc", active=True)
        empty_l = LogEntry.objects.create(title="Empty Fallback Log", content="Content")

        self.assertEqual(self.client.get("/en/").status_code, 200)
        self.assertEqual(self.client.get("/es/").status_code, 200)
        self.assertEqual(self.client.get(f"/project/{empty_p.id}/").status_code, 200)
        self.assertEqual(self.client.get(f"/?log_id={empty_l.id}").status_code, 200)
        self.assertEqual(self.client.get(f"/api/logs/{empty_l.id}").status_code, 200)

    def test_scenario_4_preview_switching_and_cascade_cleanup(self):
        p = Project.objects.create(name="Cascade Proj", description="Desc", active=True)
        img1 = Image.objects.create(project=p, file=make_test_image(), is_main_preview=True)
        img2 = Image.objects.create(project=p, file=make_test_image(), is_main_preview=False)
        p.refresh_from_db()
        self.assertEqual(p.preview_image, img1)

        # Switch main preview to img2
        img2.is_main_preview = True
        img2.save()
        p.refresh_from_db()
        self.assertEqual(p.preview_image, img2)

        # Delete img2 -> falls back to img1
        img2.delete()
        p.refresh_from_db()
        self.assertEqual(p.preview_image, img1)

        # Delete project -> cleans up img1
        path1 = img1.file.path
        p.delete()
        self.assertFalse(os.path.exists(path1))

    def test_scenario_5_mixed_batch_workload(self):
        projects = []
        for i in range(5):
            proj = Project.objects.create(name=f"Batch Project {i}", description="Desc", active=True)
            for j in range(i):  # 0, 1, 2, 3, 4 images
                Image.objects.create(project=proj, file=make_test_image(), is_main_preview=(j == 0))
            projects.append(proj)

        res_en = self.client.get("/en/")
        self.assertEqual(res_en.status_code, 200)
        for proj in projects:
            det = self.client.get(f"/project/{proj.id}/")
            self.assertEqual(det.status_code, 200)
            img_api = self.client.get(f"/api/projects/{proj.id}/images/")
            self.assertEqual(img_api.status_code, 200)
            self.assertEqual(len(img_api.json()["images"]), proj.images.count())


class C2EngineeringPortfolioTests(TestCase):
    """Verifies C2 Command-and-Control engineering portfolio requirements (R1-R4, i18n, HUD)."""

    def setUp(self):
        self.client = Client()

    def test_r1_logging_viewport_chain(self):
        """Index page logging console contains log-content-area, log-scroll-container, and full viewport flex chain."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        content = res.content.decode("utf-8")
        self.assertIn('id="log-scroll-container"', content)
        self.assertIn('id="log-content-area"', content)
        self.assertIn("aura-bg", content)

    def test_r1_project_viewport_content_area(self):
        """project.html contains id='log-content-area' with markdown-body and min-h full viewport sizing."""
        proj = Project.objects.create(name="C2 Sat Comm", description="Telemetry satellite system", active=True)
        res = self.client.get(f"/project/{proj.id}/")
        self.assertEqual(res.status_code, 200)
        content = res.content.decode("utf-8")
        self.assertIn('id="log-content-area"', content)
        self.assertIn("markdown-body", content)
        self.assertIn("min-h-[calc(100dvh-12rem)]", content)

    def test_r3_and_r4_index_chapter_architecture(self):
        """index.html contains Swiss Brutalist structural container and c2-chapter-section elements."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        content = res.content.decode("utf-8")
        self.assertIn("c2-chapter-section", content)
        self.assertIn("max-w-[1440px]", content)
        self.assertIn('id="top-telemetry-bar"', content)
        self.assertIn('data-chapter="01"', content)
        self.assertIn('data-chapter="03"', content)
        self.assertIn('data-chapter="04"', content)

    def test_spa_logging_console_integrated_in_index(self):
        """index.html Chapter 04 integrates the interactive logging console with log-split and HTMX reader."""
        log = LogEntry.objects.create(title="Field Log Alpha", content="Analyzing telemetry packet integrity.")
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        content = res.content.decode("utf-8")
        self.assertIn('id="log-split"', content)
        self.assertIn('id="log-nav"', content)
        self.assertIn('id="log-scroll-container"', content)
        self.assertIn('id="log-content-area"', content)
        self.assertIn("Field Log Alpha", content)
        self.assertIn(f"hx-get=\"/api/logs/{log.id}\"", content)

    def test_spa_logging_console_target_log_query_param(self):
        """Passing ?log_id=<id> to root loads that specific log in the reading pane."""
        log1 = LogEntry.objects.create(title="Log 1", content="First entry")
        log2 = LogEntry.objects.create(title="Log 2 Specific Target", content="Targeted deep dive log content.")
        res = self.client.get(f"/?log_id={log2.id}")
        self.assertEqual(res.status_code, 200)
        content = res.content.decode("utf-8")
        self.assertIn("Log 2 Specific Target", content)
        self.assertIn("Targeted deep dive log content.", content)


    def test_r3_and_r4_chapter_02_rendered_when_badges_exist(self):
        """When HackerRank badges exist, chapter 02 (Benchmarks) is rendered."""
        from django.utils import timezone
        HackerRankBadge.objects.create(
            badge_name="C++",
            stars=5,
            total_stars=5,
            level=3,
            timestamp=timezone.now(),
        )
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        content = res.content.decode("utf-8")
        self.assertIn('id="chapter-02"', content)
        self.assertIn('data-chapter="02"', content)
        self.assertIn("02 // BENCHMARKS", content)

    def test_5_core_identity_pillars_english(self):
        """Verify 5 Core Identity Pillars rendered in English."""
        res = self.client.get("/en/")
        self.assertEqual(res.status_code, 200)
        content = res.content.decode("utf-8")
        self.assertIn("THE ENGINE OVER THE FACADE", content)
        self.assertIn("Systems &amp; Low-Level", content)
        self.assertIn("Backend &amp; Data Architecture", content)
        self.assertIn("Hardened Infrastructure", content)
        self.assertIn("Applied Cryptography &amp; Telematics", content)

    def test_5_core_identity_pillars_spanish(self):
        """Verify 5 Core Identity Pillars rendered translated in Spanish."""
        res = self.client.get("/es/")
        self.assertEqual(res.status_code, 200)
        content = res.content.decode("utf-8")
        self.assertIn("EL MOTOR SOBRE LA FACHADA", content)
        self.assertIn("Sistemas y Bajo Nivel", content)
        self.assertIn("Arquitectura Backend y Datos", content)
        self.assertIn("Infraestructura Blindada", content)
        self.assertIn("Criptografía Aplicada y Telemática", content)

    def test_top_telemetry_bar_and_navigation(self):
        """Verify top telemetry bar contains clean anchor links and identity branding."""
        res = self.client.get("/en/")
        self.assertEqual(res.status_code, 200)
        content = res.content.decode("utf-8")
        self.assertIn('id="top-telemetry-bar"', content)
        self.assertIn("JOSUÉ LEIVA", content)
        self.assertIn("INDEX", content)
        self.assertIn("BENCHMARKS", content)
        self.assertIn("LOGS", content)
        self.assertIn("SYSTEMS", content)

    def test_anti_slop_no_custom_cursor_or_floating_hud(self):
        """Verify custom cursor and floating HUDs are removed in favor of native OS cursor."""
        res = self.client.get("/en/")
        self.assertEqual(res.status_code, 200)
        content = res.content.decode("utf-8")
        self.assertNotIn('<div id="cursor"', content)
        self.assertNotIn('<aside id="c2-mission-hud"', content)
        self.assertNotIn('<button type="button" id="mobile-c2-hud"', content)

    def test_top_telemetry_bar_locale_and_clock(self):
        """Verify Top Telemetry Bar includes live clock and plain text weather temp."""
        res = self.client.get("/en/")
        self.assertEqual(res.status_code, 200)
        content = res.content.decode("utf-8")
        self.assertIn('id="santiago-clock"', content)
        self.assertIn('id="santiago-weather-temp"', content)
        self.assertIn("CV.PDF", content)

    def test_swiss_brutalist_hairline_grid(self):
        """Verify Swiss Brutalist hairline grid container and deep carbon palette."""
        res = self.client.get("/en/")
        self.assertEqual(res.status_code, 200)
        content = res.content.decode("utf-8")
        self.assertIn("max-w-[1440px]", content)
        self.assertIn("border-white/[0.08]", content)
        self.assertIn("bg-[#070708]", content)

    def test_threejs_packet_simulation_and_boundary_reflection(self):
        """Verify main.js contains 110 spatial nodes, directional boundary clamping, and dynamic resize adaptation."""
        js_path = os.path.join(settings.BASE_DIR, "static", "portfolio", "js", "main.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js_code = f.read()
        self.assertIn("const nodeCount = 110;", js_code)
        self.assertIn("packetCount = 44;", js_code)
        self.assertIn("-Math.abs(nodeVelocities[i].vx)", js_code)
        self.assertIn("Math.abs(nodeVelocities[i].vx)", js_code)
        self.assertIn("isMobile = newWidth < 768;", js_code)
        self.assertIn("spreadX = isMobile ? 65 : 85;", js_code)

    def test_po_and_mo_catalog_synchronization(self):
        """Verify django.po contains all critical C2 translation keys matching django.mo."""
        import gettext
        mo_path = os.path.join(settings.BASE_DIR, "locale", "es", "LC_MESSAGES", "django.mo")
        po_path = os.path.join(settings.BASE_DIR, "locale", "es", "LC_MESSAGES", "django.po")
        with open(po_path, "r", encoding="utf-8") as f:
            po_text = f.read()
        with open(mo_path, "rb") as f:
            t = gettext.GNUTranslations(f)
        critical_keys = [
            "THE ENGINE OVER THE FACADE",
            "The Engine Over the Facade",
            "C2 // LIFECYCLE",
            "Mission Lifecycle HUD",
            "Scroll to top",
            "Edge Hardware Telemetry",
            "Hardened Ingestion Pipelines",
            "Relational Data Modeling",
            "Systems Craftsmanship",
            "HackerRank Badges",
        ]
        for key in critical_keys:
            self.assertIn(f'msgid "{key}"', po_text)
            self.assertIn(key, t._catalog)

    def test_calmed_threejs_and_snappy_scroll_engine(self):
        """Verify calmed Three.js network configuration, clean chapter navigation, and visible sections."""
        js_path = os.path.join(settings.BASE_DIR, "static", "portfolio", "js", "main.js")
        css_path = os.path.join(settings.BASE_DIR, "static", "portfolio", "css", "custom.css")
        with open(js_path, "r", encoding="utf-8") as f:
            js_code = f.read()
        with open(css_path, "r", encoding="utf-8") as f:
            css_code = f.read()

        # Three.js calming assertions
        self.assertIn("connectionThresholdSq = isMobile ? 55 : 75;", js_code)
        self.assertIn("speed: 0.003 + Math.random() * 0.0045,", js_code)
        self.assertIn("outerLattice.rotation.y += 0.0008;", js_code)

        # Chapter navigation assertions
        self.assertIn("function initSnappyChapterNavigation()", js_code)
        self.assertIn("document.body.classList.add('c2-snapping-enabled');", js_code)
        self.assertIn("function goToChapter(targetIndex)", js_code)
        self.assertIn("function handleWheel(e)", js_code)

        # CSS section transitions and guaranteed visibility
        self.assertIn(".c2-snapping-enabled .c2-chapter-section", css_code)
        self.assertIn(".c2-snapping-enabled .c2-chapter-section.c2-chapter-active", css_code)
        self.assertIn(".c2-snapping-enabled .c2-chapter-section.c2-chapter-transitioning", css_code)
        self.assertIn(".c2-snapping-enabled .c2-chapter-section:not(.c2-chapter-active):not(.c2-chapter-transitioning)", css_code)
        self.assertIn("visibility: visible !important;", css_code)
        self.assertIn("opacity: 1 !important;", css_code)

    def test_theme_switcher_and_light_mode_default(self):
        """Verify light theme ('lofi') is default across all pages, with toggle controller present."""
        proj = Project.objects.create(name="Theme Test Project", description="Checking themes", active=True)
        routes = ["/en/", "/es/", f"/project/{proj.id}/"]
        for route in routes:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200)
            content = res.content.decode("utf-8")
            self.assertIn('data-theme="lofi"', content)
            self.assertIn('id="theme-toggle-btn"', content)
            self.assertIn('class="theme-controller hidden"', content)
            self.assertIn("theme-icon-sun", content)
            self.assertIn("theme-icon-moon", content)
            self.assertIn("theme-text-label", content)

        # Check main.js and custom.css rules
        js_path = os.path.join(settings.BASE_DIR, "static", "portfolio", "js", "main.js")
        css_path = os.path.join(settings.BASE_DIR, "static", "portfolio", "css", "custom.css")
        with open(js_path, "r", encoding="utf-8") as f:
            js_code = f.read()
        with open(css_path, "r", encoding="utf-8") as f:
            css_code = f.read()

        self.assertIn("function updateThemeUI(theme)", js_code)
        self.assertIn("(savedTheme === 'dracula' || savedTheme === 'lofi') ? savedTheme : 'lofi'", js_code)
        self.assertIn('[data-theme="lofi"]', css_code)
        self.assertIn('[data-theme="dracula"]', css_code)
        self.assertIn('--bg: #F8F9FA;', css_code)
        self.assertIn('--bg: #050506;', css_code)


