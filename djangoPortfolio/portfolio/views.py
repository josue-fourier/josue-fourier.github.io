import hmac
import json
import threading
import urllib.request
from typing import override

from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
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
            .order_by("order", "id")
        )
        context["technical_strengths"] = (
            TechnicalStrength.objects.all()
            .annotate(project_count=Count("project", filter=Q(project__active=True)))
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
# Health check
# ---------------------------------------------------------


def health_check(request):
    """Health check route returning HTTP 200 OK."""
    return JsonResponse({"status": "healthy"})


def _has_valid_token(request, env_key, header):
    """Fails closed: no configured token means nobody is authorized."""
    configured_token = config(env_key, default="").strip()
    auth = request.headers.get("Authorization", "")
    provided_token = (
        request.headers.get(header)
        or (auth[len("Bearer "):] if auth.startswith("Bearer ") else "")
    ).strip()
    return bool(configured_token) and hmac.compare_digest(provided_token, configured_token)


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



def track_download(request, name):
    """Receives nginx's mirrored PDF requests and reports them to Umami as events, preserving visitor UA/IP/referrer."""
    if name not in ("cv-en", "cv-es"):
        raise Http404
    host = request.get_host().split(":")[0]
    body = json.dumps({"type": "event", "payload": {
        "website": config("UMAMI_WEBSITE_ID", default="31434b15-eee1-4168-8f9f-bd302c62124a"),
        "hostname": host,
        "url": f"/{name}",
        "name": "cv-pdf-served",
        "data": {"lang": name[-2:], "source": "direct-url"},
        "referrer": request.headers.get("Referer", ""),
        "language": request.headers.get("Accept-Language", "").split(",")[0],
    }}).encode()
    headers = {"Content-Type": "application/json", "User-Agent": request.headers.get("User-Agent", "")}
    if xff := request.headers.get("X-Forwarded-For"):
        headers["X-Forwarded-For"] = xff

    def send():
        try:
            urllib.request.urlopen(urllib.request.Request(config("UMAMI_SEND_URL", default="https://analytics.proyectosos.cl/api/send"), body, headers), timeout=5)
        except Exception:
            pass  # analytics must never break the site

    threading.Thread(target=send, daemon=True).start()
    return HttpResponse(status=204)
