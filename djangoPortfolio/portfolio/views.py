import hmac
import json
from typing import override

from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Count, F
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
import datetime
from decouple import config
from django.utils import timezone
from django.views.generic import TemplateView

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
        context["total_skills"] = CoreSkill.objects.count()

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

        context["total_projects"] = Project.objects.filter(active=True).count()

        # HackerRank Badges: latest available snapshot
        latest_badge = HackerRankBadge.objects.order_by("-timestamp").first()
        if latest_badge:
            exact_matches = HackerRankBadge.objects.filter(timestamp=latest_badge.timestamp)
            if exact_matches.count() > 1:
                latest_badges = exact_matches.order_by("-stars", "-progress_to_next_star","badge_name")
            else:
                # If only 1 exact timestamp match, check for a subsecond cluster
                # (e.g. badges saved sequentially within a tight window without explicit timestamp)
                cluster = HackerRankBadge.objects.filter(
                    timestamp__gte=latest_badge.timestamp - datetime.timedelta(milliseconds=600),
                    timestamp__lte=latest_badge.timestamp,
                )
                cluster_names = list(cluster.values_list("badge_name", flat=True))
                # Ensure no duplicate badge names exist in cluster (which indicates overlapping runs)
                if len(cluster_names) > 1 and len(cluster_names) == len(set(cluster_names)):
                    latest_badges = cluster.order_by("-stars", "badge_name")
                else:
                    # Genuinely a single-badge snapshot
                    latest_badges = exact_matches.order_by("-stars", "badge_name")
        else:
            latest_badges = HackerRankBadge.objects.none()

        context["hackerrank_badges"] = latest_badges
        context["badges"] = latest_badges

        # Telemetry: Current personal status
        context["current_status"] = Status.objects.first()

        # Telemetry: Node heartbeat (only shown if recent, within 20 mins)
        latest_hb = NodeHeartbeat.objects.order_by("-timestamp").first()
        context["node_heartbeat"] = latest_hb if (latest_hb and latest_hb.is_recent) else None

        # Interactive Logging Console for SPA (Chapter 04)
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

        target_log = None
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
            except (LogEntry.DoesNotExist, ValueError, ValidationError):
                pass

        if not target_log and log_list.exists():
            import markdown

            first_log = (
                LogEntry.objects.select_related("project")
                .prefetch_related("stack", "images")
                .order_by("-date")
                .first()
            )
            if first_log:
                first_log.html_content = markdown.markdown(
                    first_log.content, extensions=["fenced_code", "tables"]
                )
                target_log = first_log

        context["target_log"] = target_log

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


def _has_valid_token(request, env_key, header):
    """Fails closed: no configured token means nobody is authorized."""
    configured_token = config(env_key, default="").strip()
    auth = request.headers.get("Authorization", "")
    provided_token = (
        request.headers.get(header)
        or (auth[len("Bearer "):] if auth.startswith("Bearer ") else "")
    ).strip()
    return bool(configured_token) and hmac.compare_digest(provided_token, configured_token)


def _image_write_forbidden(request):
    """Image API writes need IMAGE_API_TOKEN or a logged-in staff user. GET stays public."""
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return None
    if request.user.is_authenticated and request.user.is_staff:
        return None
    if _has_valid_token(request, "IMAGE_API_TOKEN", "X-API-Token"):
        return None
    return JsonResponse({"error": "Unauthorized"}, status=401)


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
    if denied := _image_write_forbidden(request):
        return denied

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
    if denied := _image_write_forbidden(request):
        return denied
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
    if denied := _image_write_forbidden(request):
        return denied
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
    if denied := _image_write_forbidden(request):
        return denied
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


@csrf_exempt
def telemetry_heartbeat(request):
    """POST /api/telemetry/heartbeat/
    Receives an arbitrary telemetry string from a remote node (e.g. Raspberry Pi)
    Authentication: Header X-Telemetry-Token: <token> or Authorization: Bearer <token>
    Payload: JSON {"status": "string"} or {"message": "string"} or raw text
    """
    if request.method != "POST":
        return HttpResponse(status=405)

    if not config("TELEMETRY_TOKEN", default="").strip():
        return JsonResponse({"error": "TELEMETRY_TOKEN not configured"}, status=403)
    if not _has_valid_token(request, "TELEMETRY_TOKEN", "X-Telemetry-Token"):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    status_text = ""
    node_name = "raspberry-pi"

    if request.content_type == "application/json" and request.body:
        try:
            data = json.loads(request.body.decode("utf-8"))
            if isinstance(data, dict):
                status_text = str(data.get("status") or data.get("message") or "")
                node_name = str(data.get("node_name") or data.get("node") or "raspberry-pi")
            elif isinstance(data, str):
                status_text = data
        except Exception:
            status_text = request.body.decode("utf-8", errors="ignore")
    else:
        status_text = (
            request.POST.get("status")
            or request.POST.get("message")
            or request.body.decode("utf-8", errors="ignore")
        )

    status_text = status_text.strip()
    if not status_text:
        return JsonResponse({"error": "Empty status payload"}, status=400)

    hb, _ = NodeHeartbeat.objects.update_or_create(
        node_name=node_name,
        defaults={
            "status": status_text,
            "timestamp": timezone.now(),
        },
    )

    return JsonResponse(
        {
            "success": True,
            "node_name": hb.node_name,
            "status": hb.status,
            "timestamp": hb.timestamp.isoformat(),
        },
        status=200,
    )

