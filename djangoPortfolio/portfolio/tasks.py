import json
import logging
import math
from typing import Any, Dict, List, Optional
import requests
from django.db import transaction
from django.utils import timezone
from huey import crontab
from huey.contrib.djhuey import db_periodic_task

from decouple import config
from .models import HackerRankBadge, Status

logger = logging.getLogger(__name__)

HACKERRANK_BADGES_URL = config(
    "HACKERRANK_BADGES_URL",
    default="https://www.hackerrank.com/rest/hackers/xmenmagnet/badges",
)


def _safe_int(
    value: Any,
    default: Optional[int] = None,
    min_val: Optional[int] = None,
    max_val: Optional[int] = 2147483647,
) -> Optional[int]:
    if value is None:
        return default
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return default
    try:
        val = int(value)
    except (ValueError, TypeError, OverflowError):
        try:
            val = int(float(value))
        except (ValueError, TypeError, OverflowError):
            return default
    if min_val is not None and val < min_val:
        return default
    if max_val is not None and val > max_val:
        return default
    return val


def _safe_float(
    value: Any,
    default: Optional[float] = None,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
) -> Optional[float]:
    if value is None:
        return default
    try:
        val = float(value)
    except (ValueError, TypeError, OverflowError):
        return default
    if math.isnan(val) or math.isinf(val):
        return default
    if min_val is not None and val < min_val:
        return default
    if max_val is not None and val > max_val:
        return default
    return val


def _safe_str(
    value: Any,
    default: Optional[str] = None,
    max_length: Optional[int] = None,
) -> Optional[str]:
    if value is None:
        return default
    s = str(value).strip()
    if not s:
        return default
    if max_length and len(s) > max_length:
        return s[:max_length]
    return s


def parse_and_save_badges(
    badge_data_list: List[Dict[str, Any]], snapshot_time: Optional[timezone.datetime] = None
) -> List[HackerRankBadge]:
    """
    Parses a list of badge dictionaries from HackerRank API and saves them
    as an atomic snapshot with snapshot_time. Tolerates null or missing fields.
    """
    if snapshot_time is None:
        snapshot_time = timezone.now()

    created_badges = []
    with transaction.atomic():
        for badge in badge_data_list:
            if not isinstance(badge, dict):
                logger.warning("Skipping non-dict badge entry: %s", badge)
                continue

            raw_url = _safe_str(badge.get("url"), max_length=500)
            if raw_url:
                if raw_url.startswith("http://") or raw_url.startswith("https://"):
                    normalized_url = raw_url[:500]
                elif raw_url.startswith("/"):
                    normalized_url = f"https://www.hackerrank.com{raw_url}"[:500]
                else:
                    normalized_url = f"https://www.hackerrank.com/{raw_url}"[:500]
            else:
                normalized_url = ""

            badge_record = HackerRankBadge(
                badge_category=_safe_str(badge.get("badge_category"), max_length=300),
                badge_type=_safe_str(badge.get("badge_type"), max_length=100),
                category_name=_safe_str(badge.get("category_name"), max_length=300),
                badge_name=_safe_str(badge.get("badge_name"), max_length=300) or "Unnamed Badge",
                badge_short_name=_safe_str(badge.get("badge_short_name"), max_length=100),
                total_stars=_safe_int(badge.get("total_stars"), default=0, min_val=0),
                total_points=_safe_int(badge.get("total_points"), min_val=0),
                url=normalized_url,
                stars=_safe_int(badge.get("stars"), default=0, min_val=0),
                level=_safe_int(badge.get("level"), default=1, min_val=1),
                current_points=_safe_float(badge.get("current_points"), default=0.0, min_val=0.0),
                progress_to_next_star=_safe_float(badge.get("progress_to_next_star"), default=0.0, min_val=0.0, max_val=1.0),
                upcoming_level=_safe_int(badge.get("upcoming_level"), min_val=1),
                solved=_safe_int(badge.get("solved"), default=0, min_val=0),
                total_challenges=_safe_int(badge.get("total_challenges"), default=0, min_val=0),
                hacker_rank=_safe_int(badge.get("hacker_rank"), min_val=0, max_val=9223372036854775807),
                timestamp=snapshot_time,
            )
            badge_record.save()
            created_badges.append(badge_record)

    return created_badges


@db_periodic_task(crontab(minute='0', hour='8'))
def update_hackerrank_badges(url: str = HACKERRANK_BADGES_URL) -> List[HackerRankBadge]:
    """
    Fetches HackerRank badges daily at 08:00 AM (America/Santiago) and
    persists them as a new snapshot in the database.
    """
    logger.info("Retrieving HackerRank badge data from %s...", url)
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "PortfolioBadgeIngestion/1.0"},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error("Network error retrieving HackerRank badges: %s", e)
        return []
    except Exception as e:
        logger.error("Unexpected error retrieving HackerRank badges: %s", e)
        return []

    try:
        if not isinstance(data, dict):
            logger.warning("Unexpected root JSON type for HackerRank badges: %s", type(data))
            return []

        if data.get("status") is False:
            logger.warning("HackerRank API returned status=False: %s", data)
            return []

        models_data = data.get("models")
        if not models_data or not isinstance(models_data, list):
            logger.warning("No valid badge models found in HackerRank API response: %s", data)
            return []

        snapshot_time = timezone.now()
        badges = parse_and_save_badges(models_data, snapshot_time=snapshot_time)
        logger.info(
            "Successfully ingested %d HackerRank badges for snapshot %s",
            len(badges),
            snapshot_time,
        )
        return badges
    except Exception as e:
        logger.error("Error parsing/saving HackerRank badges: %s", e, exc_info=True)
        return []


@db_periodic_task(crontab(minute="*/2"))
def check_ntfy_status_updates():
    """Polls ntfy container/server for new messages on NTFY_TOPIC.
    If NTFY_URL or NTFY_TOPIC is not configured, this task does nothing.
    """
    ntfy_url = config("NTFY_URL", default="").strip()
    ntfy_topic = config("NTFY_TOPIC", default="").strip()
    if not ntfy_url or not ntfy_topic:
        logger.info("NTFY polling skipped: NTFY_URL or NTFY_TOPIC not configured.")
        return None

    ntfy_token = config("NTFY_TOKEN", default="").strip()
    poll_url = f"{ntfy_url.rstrip('/')}/{ntfy_topic}/json?poll=1&since=10m"

    raw_verify = config("NTFY_VERIFY_SSL", default="true").strip()
    if raw_verify.lower() in ("false", "0", "no"):
        ntfy_verify_ssl = False
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        except Exception:
            pass
    elif raw_verify.lower() in ("true", "1", "yes"):
        ntfy_verify_ssl = True
    else:
        ntfy_verify_ssl = raw_verify

    headers = {"User-Agent": "PortfolioStatusSubscriber/1.0"}
    if ntfy_token:
        headers["Authorization"] = f"Bearer {ntfy_token}"

    try:
        r = requests.get(poll_url, headers=headers, timeout=10, verify=ntfy_verify_ssl)
        r.raise_for_status()
    except Exception as e:
        logger.warning("ntfy poll skipped/failed: %s", e)
        return None

    created_status = None
    latest_msg = None

    for line in r.text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
            if item.get("event") == "message" and item.get("message"):
                latest_msg = item["message"].strip()
        except Exception:
            continue

    if latest_msg:
        current = Status.objects.first()
        if not current or current.message != latest_msg:
            created_status = Status.objects.create(
                message=latest_msg,
                source="ntfy",
            )
            logger.info("New Status received from ntfy: %s", latest_msg)

    return created_status

