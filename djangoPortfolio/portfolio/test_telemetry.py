import datetime
import json
from unittest.mock import MagicMock, patch

from django.test import Client, TestCase, override_settings
from django.utils import timezone

from portfolio.models import NodeHeartbeat, Status
from portfolio.tasks import check_ntfy_status_updates


class StatusAndHeartbeatModelTests(TestCase):
    def test_status_creation_and_ordering(self):
        s1 = Status.objects.create(message="Status 1", source="admin")
        s2 = Status.objects.create(message="Status 2", source="ntfy")

        latest = Status.objects.first()
        self.assertEqual(latest.message, "Status 2")
        self.assertIn("Status 2", str(s2))

    def test_node_heartbeat_is_recent(self):
        recent_hb = NodeHeartbeat.objects.create(
            node_name="pi-test",
            status="PI-4 // 42C // UPTIME 10d",
            timestamp=timezone.now(),
        )
        self.assertTrue(recent_hb.is_recent)

        # Stale heartbeat (30 minutes ago)
        stale_time = timezone.now() - datetime.timedelta(minutes=30)
        stale_hb = NodeHeartbeat.objects.create(
            node_name="pi-stale",
            status="OLD REPORT",
        )
        NodeHeartbeat.objects.filter(pk=stale_hb.pk).update(timestamp=stale_time)
        stale_hb.refresh_from_db()
        self.assertFalse(stale_hb.is_recent)


class TelemetryEndpointTests(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("portfolio.views.config")
    def test_telemetry_heartbeat_unauthorized(self, mock_config):
        mock_config.side_effect = lambda key, default="": "secret-token-123" if key == "TELEMETRY_TOKEN" else default

        # No token
        res = self.client.post(
            "/api/telemetry/heartbeat/",
            data=json.dumps({"status": "NODE ACTIVE"}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 401)

        # Wrong token
        res = self.client.post(
            "/api/telemetry/heartbeat/",
            data=json.dumps({"status": "NODE ACTIVE"}),
            content_type="application/json",
            HTTP_X_TELEMETRY_TOKEN="wrong-token",
        )
        self.assertEqual(res.status_code, 401)

    @patch("portfolio.views.config")
    def test_telemetry_heartbeat_success_json(self, mock_config):
        mock_config.side_effect = lambda key, default="": "secret-token-123" if key == "TELEMETRY_TOKEN" else default

        payload = {"status": "PI-4 // CPU: 39°C // UPTIME: 5d", "node_name": "homelab-pi"}
        res = self.client.post(
            "/api/telemetry/heartbeat/",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_TELEMETRY_TOKEN="secret-token-123",
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["node_name"], "homelab-pi")
        self.assertEqual(data["status"], payload["status"])

        # Check DB
        hb = NodeHeartbeat.objects.get(node_name="homelab-pi")
        self.assertEqual(hb.status, payload["status"])

    @patch("portfolio.views.config")
    def test_telemetry_heartbeat_updates_existing_node(self, mock_config):
        mock_config.side_effect = lambda key, default="": "secret-token-123" if key == "TELEMETRY_TOKEN" else default

        # First post
        self.client.post(
            "/api/telemetry/heartbeat/",
            data=json.dumps({"status": "BOOTING", "node_name": "rpi"}),
            content_type="application/json",
            HTTP_X_TELEMETRY_TOKEN="secret-token-123",
        )
        # Second post (updates same node)
        self.client.post(
            "/api/telemetry/heartbeat/",
            data=json.dumps({"status": "RUNNING OK", "node_name": "rpi"}),
            content_type="application/json",
            HTTP_X_TELEMETRY_TOKEN="secret-token-123",
        )
        self.assertEqual(NodeHeartbeat.objects.filter(node_name="rpi").count(), 1)
        self.assertEqual(NodeHeartbeat.objects.get(node_name="rpi").status, "RUNNING OK")


class TelemetryIndexViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_hero_renders_personal_status_when_available(self):
        Status.objects.create(message="Building telemetry pipelines", source="admin")
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Building telemetry pipelines", res.content.decode("utf-8"))
        self.assertIn("STATUS:", res.content.decode("utf-8"))

    def test_hero_renders_recent_heartbeat(self):
        NodeHeartbeat.objects.create(
            node_name="pi-live",
            status="PI-4 // 41°C // ONLINE",
            timestamp=timezone.now(),
        )
        res = self.client.get("/")
        content = res.content.decode("utf-8")
        self.assertIn("PI-4 // 41°C // ONLINE", content)
        self.assertIn("NODE:", content)

    def test_hero_hides_stale_heartbeat(self):
        stale_time = timezone.now() - datetime.timedelta(minutes=45)
        hb = NodeHeartbeat.objects.create(
            node_name="pi-old",
            status="STALE HEARTBEAT THAT MUST BE HIDDEN",
        )
        NodeHeartbeat.objects.filter(pk=hb.pk).update(timestamp=stale_time)

        res = self.client.get("/")
        content = res.content.decode("utf-8")
        self.assertNotIn("STALE HEARTBEAT THAT MUST BE HIDDEN", content)


class NtfyTaskTests(TestCase):
    @patch("portfolio.tasks.config")
    def test_ntfy_task_noop_when_not_configured(self, mock_config):
        mock_config.side_effect = lambda key, default="": ""
        result = check_ntfy_status_updates.call_local()
        self.assertIsNone(result)

    @patch("portfolio.tasks.requests.get")
    @patch("portfolio.tasks.config")
    def test_ntfy_task_creates_status_on_new_message(self, mock_config, mock_get):
        mock_config.side_effect = lambda key, default="": {
            "NTFY_URL": "http://ntfy:80",
            "NTFY_TOPIC": "my-status",
            "NTFY_TOKEN": "",
        }.get(key, default)

        mock_resp = MagicMock()
        mock_resp.text = json.dumps({"event": "message", "message": "Deploying from my phone via ntfy!"})
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        result = check_ntfy_status_updates.call_local()
        self.assertIsNotNone(result)
        self.assertEqual(result.message, "Deploying from my phone via ntfy!")
        self.assertEqual(result.source, "ntfy")

        # Second poll with same message should not duplicate
        dup_result = check_ntfy_status_updates.call_local()
        self.assertIsNone(dup_result)
        self.assertEqual(Status.objects.count(), 1)
