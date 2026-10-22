from .models import NodeHeartbeat, Status


def global_telemetry(request):
    """Provides global telemetry context variables for navbar ticker and base templates."""
    latest_hb = NodeHeartbeat.objects.order_by("-timestamp").first()
    node_hb = latest_hb if (latest_hb and latest_hb.is_recent) else None
    ntfy_msg = Status.objects.filter(source="ntfy").order_by("-timestamp").first()
    latest_status = Status.objects.first()

    return {
        "node_heartbeat": node_hb,
        "ntfy_message": ntfy_msg,
        "current_status": latest_status,
        "global_node_heartbeat": node_hb,
        "global_ntfy_message": ntfy_msg,
        "global_current_status": latest_status,
    }
