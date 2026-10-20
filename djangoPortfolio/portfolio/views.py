import json
from typing import override

from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Count, F
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from .models import Image, LogEntry, Project, SkillCategory, TechnicalStrength


class RootPage(TemplateView):
    template_name = "portfolio/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["projects"] = (
            Project.objects.filter(active=True)
            .prefetch_related("stack", "images")
            .annotate(stack_count=Count("stack"))
            .order_by("-stack_count")
        )
        context["technical_strengths"] = (
            TechnicalStrength.objects.all()
            .annotate(project_count=Count("project"))
            .filter(project_count__gt=0)
            .order_by("-project_count")
        )
        context["core_competencies"] = SkillCategory.objects.prefetch_related("skills").all()

        # Featured logs
        featured_logs = (
            LogEntry.objects.filter(is_featured=True)
            .select_related("project")
            .prefetch_related("stack", "images")
            .order_by("-date")
        )
        context["featured_logs"] = featured_logs

        if featured_logs.exists():
            featured_ids = [log.id for log in featured_logs]
            context["latest_logs"] = (
                LogEntry.objects.exclude(id__in=featured_ids)
                .select_related("project")
                .prefetch_related("stack", "images")
                .order_by("-date")[:3]
            )
        else:
            context["latest_logs"] = (
                LogEntry.objects.select_related("project")
                .prefetch_related("stack", "images")
                .order_by("-date")[:3]
            )

        context["total_projects"] = Project.objects.count()

        return context


class LoggingView(TemplateView):
    template_name = "portfolio/logging.html"

    @override
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        log_list = (
            LogEntry.objects.defer("content")
            .select_related("project")
            .prefetch_related("stack")
            .order_by("-date")
        )
        paginator = Paginator(log_list, 10)
        context["page_obj"] = paginator.get_page(1)
        context["log_count"] = LogEntry.objects.count()

        target_log_id = self.request.GET.get("log_id")
        context["target_log_id"] = target_log_id

        if target_log_id:
            try:
                import markdown

                target_log = (
                    LogEntry.objects.select_related("project")
                    .prefetch_related("stack", "images")
                    .get(id=target_log_id)
                )
                target_log.html_content = markdown.markdown(
                    target_log.content, extensions=["fenced_code", "tables"]
                )
                context["target_log"] = target_log
            except (LogEntry.DoesNotExist, ValueError, ValidationError):
                pass

        return context


def single_log(request, log_id):
    if request.method == "GET":
        import markdown

        log = get_object_or_404(
            LogEntry.objects.select_related("project").prefetch_related("stack", "images"),
            id=log_id,
        )

        # Parse markdown to HTML
        log.html_content = markdown.markdown(
            log.content, extensions=["fenced_code", "tables"]
        )

        context = {"log": log}

        return render(
            request, "portfolio/_log.html", context, content_type="text/html"
        )

    return HttpResponse(status=405)


def log_list(request):
    if request.method == "GET":
        queryset = (
            LogEntry.objects.defer("content")
            .select_related("project")
            .prefetch_related("stack")
            .order_by("-date")
        )
        paginator = Paginator(queryset, 10)

        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(
            request,
            "portfolio/_log_nav_partial.html",
            {"page_obj": page_obj},
        )

    return HttpResponse(status=405)


def project_detail(request, project_id):
    if request.method == "GET":
        import markdown

        project = get_object_or_404(
            Project.objects.prefetch_related("stack", "images"), id=project_id
        )

        # Parse markdown to HTML if content exists
        if project.content:
            project.html_content = markdown.markdown(
                project.content, extensions=["fenced_code", "tables"]
            )
        else:
            project.html_content = ""

        context = {"project": project}

        return render(
            request, "portfolio/project.html", context, content_type="text/html"
        )

    return HttpResponse(status=405)


# ---------------------------------------------------------
# Health check & Image API Endpoints
# ---------------------------------------------------------


def health_check(request):
    """Health check route returning HTTP 200 OK."""
    return JsonResponse({"status": "healthy"})


def image_to_dict(image):
    """Serializes Image model instance to JSON-serializable dictionary."""
    return {
        "id": str(image.id),
        "url": image.file.url if image.file else None,
        "project_id": image.project_id,
        "log_id": str(image.log_id) if image.log_id else None,
        "is_main_preview": image.is_main_preview,
        "alt_text": image.alt_text,
        "caption": image.caption,
        "order": image.order,
        "created_at": image.created_at.isoformat() if image.created_at else None,
    }


def _parse_payload(request):
    """Helper to parse JSON body or POST form data."""
    if request.content_type == "application/json" and request.body:
        try:
            return json.loads(request.body.decode("utf-8"))
        except Exception:
            return {}
    return request.POST


@csrf_exempt
def image_upload(request):
    """POST /api/images/upload/
    Accepts multipart file upload with optional project_id, log_id, is_main_preview,
    alt_text, caption, order.
    Returns 201 Created with JSON image metadata or 400 on error.
    """
    if request.method != "POST":
        return HttpResponse(status=405)

    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    data = _parse_payload(request)

    project = None
    project_id = data.get("project_id") or request.POST.get("project_id")
    if project_id:
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse({"error": "Project not found"}, status=404)
        except (ValueError, TypeError, ValidationError):
            return JsonResponse({"error": "Invalid project_id"}, status=400)

    log = None
    log_id = data.get("log_id") or request.POST.get("log_id")
    if log_id:
        try:
            log = LogEntry.objects.get(id=log_id)
        except LogEntry.DoesNotExist:
            return JsonResponse({"error": "Log not found"}, status=404)
        except (ValueError, TypeError, ValidationError):
            return JsonResponse({"error": "Invalid log_id"}, status=400)

    is_main_raw = (
        data.get("is_main_preview")
        if "is_main_preview" in data
        else request.POST.get("is_main_preview", "")
    )
    is_main = str(is_main_raw).lower() in ("true", "1", "yes")

    alt_text = str(data.get("alt_text", request.POST.get("alt_text", "")))
    caption = str(data.get("caption", request.POST.get("caption", "")))

    try:
        order = int(data.get("order", request.POST.get("order", 0)))
    except (ValueError, TypeError):
        order = 0

    image = Image(
        file=uploaded_file,
        project=project,
        log=log,
        is_main_preview=is_main,
        alt_text=alt_text,
        caption=caption,
        order=order,
    )

    try:
        image.full_clean()
        image.save()
    except ValidationError as e:
        error_msg = e.message_dict if hasattr(e, "message_dict") else str(e)
        return JsonResponse({"error": f"Invalid image: {error_msg}"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Failed to save image: {str(e)}"}, status=400)

    return JsonResponse(image_to_dict(image), status=201)


@csrf_exempt
def image_detail(request, image_id):
    """GET /api/images/<uuid:image_id>/
    PATCH /api/images/<uuid:image_id>/
    DELETE /api/images/<uuid:image_id>/
    """
    try:
        image = Image.objects.get(id=image_id)
    except (Image.DoesNotExist, ValueError, ValidationError):
        return JsonResponse({"error": "Image not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(image_to_dict(image))

    elif request.method in ("PATCH", "PUT"):
        data = _parse_payload(request)
        if "project_id" in data:
            pid = data.get("project_id")
            if pid is None or pid == "":
                image.project = None
            else:
                try:
                    image.project = Project.objects.get(id=pid)
                except Project.DoesNotExist:
                    return JsonResponse({"error": "Project not found"}, status=404)
                except (ValueError, TypeError, ValidationError):
                    return JsonResponse({"error": "Invalid project_id"}, status=400)
        if "log_id" in data:
            lid = data.get("log_id")
            if lid is None or lid == "":
                image.log = None
            else:
                try:
                    image.log = LogEntry.objects.get(id=lid)
                except LogEntry.DoesNotExist:
                    return JsonResponse({"error": "Log not found"}, status=404)
                except (ValueError, TypeError, ValidationError):
                    return JsonResponse({"error": "Invalid log_id"}, status=400)
        if "is_main_preview" in data:
            image.is_main_preview = str(data.get("is_main_preview")).lower() in (
                "true",
                "1",
                "yes",
            )
        if "alt_text" in data:
            image.alt_text = str(data.get("alt_text", ""))
        if "caption" in data:
            image.caption = str(data.get("caption", ""))
        if "order" in data:
            try:
                image.order = int(data.get("order", 0))
            except (ValueError, TypeError):
                pass
        try:
            if not image.file:
                image.full_clean(exclude=["file"])
            else:
                image.full_clean()
            image.save()
        except ValidationError as e:
            error_msg = e.message_dict if hasattr(e, "message_dict") else str(e)
            return JsonResponse({"error": f"Invalid image: {error_msg}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Failed to save image: {str(e)}"}, status=400)
        return JsonResponse(image_to_dict(image))

    elif request.method == "DELETE":
        image.delete()
        return HttpResponse(status=204)

    return HttpResponse(status=405)


@csrf_exempt
def project_images(request, project_id):
    """GET /api/projects/<int:project_id>/images/
    POST /api/projects/<int:project_id>/images/
    """
    try:
        project = Project.objects.get(id=project_id)
    except (Project.DoesNotExist, ValueError, ValidationError):
        return JsonResponse({"error": "Project not found"}, status=404)

    if request.method == "GET":
        images = project.images.all()
        return JsonResponse({"images": [image_to_dict(img) for img in images]})

    elif request.method == "POST":
        data = _parse_payload(request)
        image_id = data.get("image_id") or request.POST.get("image_id")
        is_main_raw = (
            data.get("is_main_preview")
            if "is_main_preview" in data
            else request.POST.get("is_main_preview", "")
        )
        is_main = str(is_main_raw).lower() in ("true", "1", "yes")

        # If attaching existing image by ID
        if image_id:
            try:
                image = Image.objects.get(id=image_id)
            except Image.DoesNotExist:
                return JsonResponse({"error": "Image not found"}, status=404)
            except (ValueError, TypeError, ValidationError):
                return JsonResponse({"error": "Invalid image_id"}, status=400)
            image.project = project
            if "is_main_preview" in data or "is_main_preview" in request.POST:
                image.is_main_preview = is_main
            if "order" in data or "order" in request.POST:
                try:
                    image.order = int(data.get("order", request.POST.get("order", 0)))
                except (ValueError, TypeError):
                    pass
            if "alt_text" in data or "alt_text" in request.POST:
                image.alt_text = str(data.get("alt_text", request.POST.get("alt_text", "")))
            if "caption" in data or "caption" in request.POST:
                image.caption = str(data.get("caption", request.POST.get("caption", "")))
            try:
                if not image.file:
                    image.full_clean(exclude=["file"])
                else:
                    image.full_clean()
                image.save()
            except ValidationError as e:
                error_msg = e.message_dict if hasattr(e, "message_dict") else str(e)
                return JsonResponse({"error": f"Invalid image: {error_msg}"}, status=400)
            except Exception as e:
                return JsonResponse({"error": f"Failed to save image: {str(e)}"}, status=400)
            return JsonResponse(image_to_dict(image), status=200)

        # Direct file upload
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return JsonResponse({"error": "No file or image_id provided"}, status=400)

        alt_text = str(data.get("alt_text", request.POST.get("alt_text", "")))
        caption = str(data.get("caption", request.POST.get("caption", "")))
        try:
            order = int(data.get("order", request.POST.get("order", 0)))
        except (ValueError, TypeError):
            order = 0

        image = Image(
            file=uploaded_file,
            project=project,
            is_main_preview=is_main,
            alt_text=alt_text,
            caption=caption,
            order=order,
        )

        try:
            image.full_clean()
            image.save()
        except ValidationError as e:
            error_msg = e.message_dict if hasattr(e, "message_dict") else str(e)
            return JsonResponse({"error": f"Invalid image: {error_msg}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Failed to save image: {str(e)}"}, status=400)

        return JsonResponse(image_to_dict(image), status=201)

    return HttpResponse(status=405)


@csrf_exempt
def log_images(request, log_id):
    """GET /api/logs/<uuid:log_id>/images/
    POST /api/logs/<uuid:log_id>/images/
    """
    try:
        log = LogEntry.objects.get(id=log_id)
    except (LogEntry.DoesNotExist, ValueError, ValidationError):
        return JsonResponse({"error": "Log not found"}, status=404)

    if request.method == "GET":
        images = log.images.all()
        return JsonResponse({"images": [image_to_dict(img) for img in images]})

    elif request.method == "POST":
        data = _parse_payload(request)
        image_id = data.get("image_id") or request.POST.get("image_id")

        if image_id:
            try:
                image = Image.objects.get(id=image_id)
            except Image.DoesNotExist:
                return JsonResponse({"error": "Image not found"}, status=404)
            except (ValueError, TypeError, ValidationError):
                return JsonResponse({"error": "Invalid image_id"}, status=400)
            image.log = log
            if "order" in data or "order" in request.POST:
                try:
                    image.order = int(data.get("order", request.POST.get("order", 0)))
                except (ValueError, TypeError):
                    pass
            if "alt_text" in data or "alt_text" in request.POST:
                image.alt_text = str(data.get("alt_text", request.POST.get("alt_text", "")))
            if "caption" in data or "caption" in request.POST:
                image.caption = str(data.get("caption", request.POST.get("caption", "")))
            try:
                if not image.file:
                    image.full_clean(exclude=["file"])
                else:
                    image.full_clean()
                image.save()
            except ValidationError as e:
                error_msg = e.message_dict if hasattr(e, "message_dict") else str(e)
                return JsonResponse({"error": f"Invalid image: {error_msg}"}, status=400)
            except Exception as e:
                return JsonResponse({"error": f"Failed to save image: {str(e)}"}, status=400)
            return JsonResponse(image_to_dict(image), status=200)

        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return JsonResponse({"error": "No file or image_id provided"}, status=400)

        alt_text = str(data.get("alt_text", request.POST.get("alt_text", "")))
        caption = str(data.get("caption", request.POST.get("caption", "")))
        try:
            order = int(data.get("order", request.POST.get("order", 0)))
        except (ValueError, TypeError):
            order = 0

        image = Image(
            file=uploaded_file,
            log=log,
            alt_text=alt_text,
            caption=caption,
            order=order,
        )

        try:
            image.full_clean()
            image.save()
        except ValidationError as e:
            error_msg = e.message_dict if hasattr(e, "message_dict") else str(e)
            return JsonResponse({"error": f"Invalid image: {error_msg}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Failed to save image: {str(e)}"}, status=400)

        return JsonResponse(image_to_dict(image), status=201)

    return HttpResponse(status=405)
