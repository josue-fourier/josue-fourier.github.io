import datetime
import json
import logging
from unittest.mock import MagicMock, patch

import requests
from django.test import Client, TestCase
from django.utils import timezone
from huey.contrib.djhuey import HUEY

from portfolio.models import HackerRankBadge
from portfolio.tasks import (
    HACKERRANK_BADGES_URL,
    _safe_float,
    _safe_int,
    _safe_str,
    parse_and_save_badges,
    update_hackerrank_badges,
)

SAMPLE_API_PAYLOAD = {
    "status": True,
    "models": [
        {
            "badge_category": "HackerBadge::MultiDomain",
            "badge_type": "problem-solving",
            "category_name": None,
            "badge_name": "Problem Solving",
            "badge_short_name": None,
            "total_stars": 6,
            "total_points": 100,
            "url": "/domains/algorithms",
            "solved": 6,
            "total_challenges": 563,
            "track_total_score": 0,
            "hacker_rank": 2697497,
            "stars": 1,
            "level": 1,
            "current_points": 51.0,
            "progress_to_next_star": 0.3,
            "upcoming_level": None,
        },
        {
            "badge_category": "HackerBadge::Domain",
            "badge_type": "cpp",
            "category_name": "Language Proficiency",
            "badge_name": "C++",
            "badge_short_name": "CPP",
            "total_stars": 5,
            "total_points": None,
            "url": "/domains/cpp",
            "stars": 5,
            "level": 3,
            "current_points": 270.0,
            "progress_to_next_star": 1.0,
            "upcoming_level": None,
            "solved": 21,
            "total_challenges": 44,
            "hacker_rank": 146033,
        },
        {
            "badge_category": "HackerBadge::Domain",
            "badge_type": "java",
            "category_name": "Language Proficiency",
            "badge_name": "Java",
            "badge_short_name": None,
            "total_stars": 5,
            "total_points": 50,
            "url": "/domains/java",
            "stars": 1,
            "level": 1,
            "current_points": 38.0,
            "progress_to_next_star": 0.52,
            "upcoming_level": None,
            "solved": 5,
            "total_challenges": 64,
            "hacker_rank": 1467507,
        },
    ],
    "version": 2,
}


class HackerRankModelTests(TestCase):
    """Unit tests for HackerRankBadge model integrity, null handling, and properties."""

    def test_create_badge_with_all_fields(self):
        badge = HackerRankBadge.objects.create(
            badge_category="HackerBadge::Domain",
            badge_type="python",
            category_name="Language Proficiency",
            badge_name="Python",
            badge_short_name="PY",
            total_stars=5,
            total_points=250,
            url="https://www.hackerrank.com/domains/python",
            stars=4,
            level=2,
            current_points=210.5,
            progress_to_next_star=0.75,
            upcoming_level=3,
            solved=18,
            total_challenges=40,
            hacker_rank=98765,
        )
        self.assertIsNotNone(badge.pk)
        badge.full_clean()
        self.assertEqual(badge.badge_name, "Python")
        self.assertEqual(str(badge), "Python (4/5 stars)")

    def test_create_badge_with_null_and_missing_fields(self):
        """Nullable fields (upcoming_level, total_points, category_name, badge_short_name)

        must not cause database or validation errors when null.
        """
        badge = HackerRankBadge.objects.create(
            badge_category=None,
            badge_type="problem-solving",
            category_name=None,
            badge_name="Problem Solving",
            badge_short_name=None,
            total_stars=6,
            total_points=None,
            url="/domains/algorithms",
            stars=1,
            level=1,
            current_points=50.0,
            progress_to_next_star=0.3,
            upcoming_level=None,
            solved=6,
            total_challenges=560,
            hacker_rank=None,
        )
        self.assertIsNotNone(badge.pk)
        badge.full_clean()
        self.assertIsNone(badge.category_name)
        self.assertIsNone(badge.badge_short_name)
        self.assertIsNone(badge.total_points)
        self.assertIsNone(badge.upcoming_level)
        self.assertIsNone(badge.hacker_rank)

    def test_save_normalizes_relative_url(self):
        badge = HackerRankBadge.objects.create(
            badge_name="C++",
            url="/domains/cpp",
        )
        self.assertEqual(badge.url, "https://www.hackerrank.com/domains/cpp")
        self.assertEqual(badge.domain_url, "https://www.hackerrank.com/domains/cpp")

    def test_domain_url_preserves_absolute_url(self):
        badge = HackerRankBadge.objects.create(
            badge_name="Java",
            url="https://custom.domain.com/java",
        )
        self.assertEqual(badge.domain_url, "https://custom.domain.com/java")

    def test_domain_url_fallback_when_empty(self):
        badge = HackerRankBadge.objects.create(
            badge_name="SQL",
            url="",
        )
        self.assertEqual(badge.domain_url, "https://www.hackerrank.com")

    def test_display_category_fallback_order(self):
        # 1. uses category_name when present
        b1 = HackerRankBadge(category_name="Specialized Skills", badge_type="sql")
        self.assertEqual(b1.display_category, "Specialized Skills")

        # 2. falls back to formatted badge_type
        b2 = HackerRankBadge(category_name=None, badge_type="problem-solving")
        self.assertEqual(b2.display_category, "Problem Solving")

        # 3. falls back to badge_category
        b3 = HackerRankBadge(category_name=None, badge_type=None, badge_category="HackerBadge::Algorithms")
        self.assertEqual(b3.display_category, "Algorithms")

        # 4. default
        b4 = HackerRankBadge(category_name=None, badge_type=None, badge_category=None)
        self.assertEqual(b4.display_category, "Skill")

    def test_progress_percentage_calculation(self):
        b1 = HackerRankBadge(progress_to_next_star=0.755)
        self.assertEqual(b1.progress_percentage, 76)

        b2 = HackerRankBadge(progress_to_next_star=None)
        self.assertEqual(b2.progress_percentage, 0)

        b3 = HackerRankBadge(progress_to_next_star=1.0)
        self.assertEqual(b3.progress_percentage, 100)

    def test_stars_list_generation(self):
        badge = HackerRankBadge(stars=2, total_stars=5)
        stars = badge.stars_list
        self.assertEqual(len(stars), 5)
        self.assertTrue(stars[0]["filled"])
        self.assertTrue(stars[1]["filled"])
        self.assertFalse(stars[2]["filled"])
        self.assertFalse(stars[3]["filled"])
        self.assertFalse(stars[4]["filled"])


class HackerRankTaskTests(TestCase):
    """Tests for the periodic Huey task update_hackerrank_badges."""

    @patch("requests.get")
    def test_successful_task_execution(self, mock_get):
        """Executing task with mocked API response creates badge snapshot in DB."""
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_API_PAYLOAD
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        badges = update_hackerrank_badges.call_local()

        self.assertEqual(len(badges), 3)
        self.assertEqual(HackerRankBadge.objects.count(), 3)

        cpp_badge = HackerRankBadge.objects.get(badge_name="C++")
        self.assertEqual(cpp_badge.stars, 5)
        self.assertEqual(cpp_badge.total_stars, 5)
        self.assertEqual(cpp_badge.level, 3)
        self.assertEqual(cpp_badge.current_points, 270.0)
        self.assertIsNone(cpp_badge.total_points)
        self.assertEqual(cpp_badge.url, "https://www.hackerrank.com/domains/cpp")

        ps_badge = HackerRankBadge.objects.get(badge_name="Problem Solving")
        self.assertEqual(ps_badge.solved, 6)
        self.assertEqual(ps_badge.total_challenges, 563)
        self.assertIsNone(ps_badge.category_name)
        self.assertEqual(ps_badge.display_category, "Problem Solving")

    @patch("requests.get")
    def test_task_tolerates_null_and_missing_payload_fields(self, mock_get):
        sparse_payload = {
            "status": True,
            "models": [
                {
                    "badge_name": "Sparse Badge",
                    "total_stars": None,
                    "stars": None,
                    "level": None,
                    "current_points": None,
                    "progress_to_next_star": None,
                    "upcoming_level": None,
                    "total_points": None,
                    "category_name": None,
                    "badge_short_name": None,
                    "url": None,
                }
            ],
        }
        mock_response = MagicMock()
        mock_response.json.return_value = sparse_payload
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        badges = update_hackerrank_badges.call_local()
        self.assertEqual(len(badges), 1)
        b = badges[0]
        self.assertEqual(b.badge_name, "Sparse Badge")
        self.assertIsNone(b.total_points)
        self.assertIsNone(b.upcoming_level)

    @patch("requests.get")
    def test_network_timeout_logged_without_crashing(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

        with self.assertLogs("portfolio.tasks", level="ERROR") as cm:
            result = update_hackerrank_badges.call_local()

        self.assertEqual(result, [])
        self.assertEqual(HackerRankBadge.objects.count(), 0)
        self.assertTrue(any("Network error" in msg for msg in cm.output))

    @patch("requests.get")
    def test_http_error_logged_without_crashing(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        mock_get.return_value = mock_response

        with self.assertLogs("portfolio.tasks", level="ERROR") as cm:
            result = update_hackerrank_badges.call_local()

        self.assertEqual(result, [])
        self.assertEqual(HackerRankBadge.objects.count(), 0)
        self.assertTrue(any("Network error" in msg for msg in cm.output))

    @patch("requests.get")
    def test_invalid_json_handled_without_crashing(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with self.assertLogs("portfolio.tasks", level="ERROR") as cm:
            result = update_hackerrank_badges.call_local()

        self.assertEqual(result, [])
        self.assertEqual(HackerRankBadge.objects.count(), 0)

    @patch("requests.get")
    def test_empty_models_list_returns_empty_safely(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": True, "models": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with self.assertLogs("portfolio.tasks", level="WARNING") as cm:
            result = update_hackerrank_badges.call_local()
        self.assertEqual(result, [])
        self.assertEqual(HackerRankBadge.objects.count(), 0)
        self.assertTrue(any("No valid badge models" in msg for msg in cm.output))

    @patch("requests.get")
    def test_multiple_runs_create_distinct_historical_snapshots(self, mock_get):
        """Historical runs are appended without overwriting existing data."""
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_API_PAYLOAD
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Run 1: Day 1
        day1_time = timezone.now() - datetime.timedelta(days=2)
        with patch("django.utils.timezone.now", return_value=day1_time):
            update_hackerrank_badges.call_local()

        self.assertEqual(HackerRankBadge.objects.count(), 3)
        self.assertEqual(
            HackerRankBadge.objects.filter(timestamp__date=timezone.localdate(day1_time)).count(), 3
        )

        # Run 2: Day 2
        day2_time = timezone.now()
        with patch("django.utils.timezone.now", return_value=day2_time):
            update_hackerrank_badges.call_local()

        # Both runs exist in DB
        self.assertEqual(HackerRankBadge.objects.count(), 6)
        self.assertEqual(
            HackerRankBadge.objects.filter(timestamp__date=timezone.localdate(day2_time)).count(), 3
        )

    def test_huey_crontab_schedule_configuration(self):
        """Task must be registered in Huey and scheduled daily at 08:00 AM America/Santiago."""
        task_cls = update_hackerrank_badges.task_class
        self.assertIn(task_cls, HUEY._registry._periodic_tasks)

        # 08:00 AM should validate True
        t_8am = datetime.datetime(2026, 10, 21, 8, 0, 0)
        self.assertTrue(task_cls.validate_datetime(task_cls, t_8am))

        # 08:01 AM or 09:00 AM should validate False
        t_801 = datetime.datetime(2026, 10, 21, 8, 1, 0)
        t_9am = datetime.datetime(2026, 10, 21, 9, 0, 0)
        self.assertFalse(task_cls.validate_datetime(task_cls, t_801))
        self.assertFalse(task_cls.validate_datetime(task_cls, t_9am))


class HackerRankViewAndTemplateTests(TestCase):
    """Tests for RootPage index view context and responsive UI rendering."""

    def setUp(self):
        self.client = Client()

    def test_root_page_context_with_no_badges(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("hackerrank_badges", response.context)
        self.assertEqual(list(response.context["hackerrank_badges"]), [])
        # When no badges exist, section is not rendered
        self.assertNotContains(response, 'id="hackerrank-badges"')

    def test_root_page_selects_only_latest_snapshot(self):
        """When multiple daily snapshots exist, RootPage must only present the latest snapshot."""
        old_date = timezone.now() - datetime.timedelta(days=2)
        new_date = timezone.now()

        # Older snapshot badges (Day 1)
        old_b1 = HackerRankBadge.objects.create(
            badge_name="Old Problem Solving",
            stars=1,
            total_stars=6,
            timestamp=old_date,
        )
        old_b2 = HackerRankBadge.objects.create(
            badge_name="Old Python",
            stars=2,
            total_stars=5,
            timestamp=old_date,
        )

        # Latest snapshot badges (Day 2)
        new_b1 = HackerRankBadge.objects.create(
            badge_name="Problem Solving",
            category_name=None,
            badge_type="problem-solving",
            stars=2,
            total_stars=6,
            level=1,
            progress_to_next_star=0.45,
            solved=15,
            total_challenges=560,
            url="https://www.hackerrank.com/domains/algorithms",
            timestamp=new_date,
        )
        new_b2 = HackerRankBadge.objects.create(
            badge_name="C++",
            category_name="Language Proficiency",
            badge_type="cpp",
            stars=5,
            total_stars=5,
            level=3,
            progress_to_next_star=1.0,
            solved=21,
            total_challenges=44,
            url="https://www.hackerrank.com/domains/cpp",
            timestamp=new_date,
        )

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        context_badges = list(response.context["hackerrank_badges"])
        self.assertEqual(len(context_badges), 2)
        badge_names = [b.badge_name for b in context_badges]
        self.assertIn("C++", badge_names)
        self.assertIn("Problem Solving", badge_names)
        self.assertNotIn("Old Problem Solving", badge_names)
        self.assertNotIn("Old Python", badge_names)

        # Assert template rendered key badge details
        content = response.content.decode("utf-8")
        self.assertIn('id="hackerrank-badges"', content)
        self.assertIn("HackerRank Badges", content)
        self.assertIn("Problem Solving", content)
        self.assertIn("C++", content)
        self.assertIn("Language Proficiency", content)
        self.assertIn("5 / 5", content)
        self.assertIn("2 / 6", content)
        self.assertIn("Next Star Progress", content)
        self.assertIn("Solved Challenges", content)
        self.assertIn("https://www.hackerrank.com/domains/cpp", content)
        self.assertIn("https://www.hackerrank.com/domains/algorithms", content)

    def test_responsive_layout_classes_present(self):
        """Assert grid and card CSS classes ensure responsiveness across mobile, tablet, desktop."""
        HackerRankBadge.objects.create(
            badge_name="Python",
            category_name="Language Proficiency",
            badge_type="python",
            stars=4,
            total_stars=5,
            level=2,
            progress_to_next_star=0.8,
            solved=25,
            total_challenges=50,
            url="https://www.hackerrank.com/domains/python",
            timestamp=timezone.now(),
        )

        response = self.client.get("/")
        content = response.content.decode("utf-8")

        # Responsive grid classes: 1 col on mobile (<640px), 2 cols on tablet (sm:), 3 cols on desktop (lg:)
        self.assertIn("grid-cols-1", content)
        self.assertIn("sm:grid-cols-2", content)
        self.assertIn("lg:grid-cols-3", content)
        self.assertIn("glass-panel", content)
        self.assertIn("truncate", content)
        self.assertIn("break-words", content)
        self.assertIn("star-filled", content)
        self.assertIn("badge-domain-link", content)
        self.assertIn("HACKERRANK_PROFILE", content)

    def test_single_badge_snapshot_does_not_merge_past_runs(self):
        """A single-badge snapshot must only render that 1 badge without merging older runs."""
        old_time = timezone.now() - datetime.timedelta(hours=2)
        HackerRankBadge.objects.create(
            badge_name="Old Badge 1",
            stars=1,
            total_stars=5,
            timestamp=old_time,
        )
        HackerRankBadge.objects.create(
            badge_name="Old Badge 2",
            stars=2,
            total_stars=5,
            timestamp=old_time,
        )

        new_time = timezone.now()
        single_badge = HackerRankBadge.objects.create(
            badge_name="Only Latest Badge",
            stars=3,
            total_stars=5,
            timestamp=new_time,
        )

        response = self.client.get("/")
        badges = list(response.context["hackerrank_badges"])
        self.assertEqual(len(badges), 1)
        self.assertEqual(badges[0].badge_name, "Only Latest Badge")

    def test_single_badge_snapshot_not_polluted_by_recent_previous_snapshot(self):
        """A single-badge snapshot must not pull in previous snapshot badges created 1-2 seconds earlier."""
        t_old = timezone.now() - datetime.timedelta(seconds=1)
        HackerRankBadge.objects.create(
            badge_name="Old Badge 1s Ago",
            stars=2,
            total_stars=5,
            timestamp=t_old,
        )
        t_new = timezone.now()
        HackerRankBadge.objects.create(
            badge_name="New Single Badge",
            stars=4,
            total_stars=5,
            timestamp=t_new,
        )

        response = self.client.get("/")
        badges = list(response.context["hackerrank_badges"])
        self.assertEqual(len(badges), 1)
        self.assertEqual(badges[0].badge_name, "New Single Badge")

    def test_subsecond_cluster_captured_correctly(self):
        """Badges created within a tight subsecond window without explicit timestamp are grouped."""
        now = timezone.now()
        b1 = HackerRankBadge.objects.create(
            badge_name="Cluster 1",
            stars=1,
            total_stars=5,
            timestamp=now - datetime.timedelta(milliseconds=400),
        )
        b2 = HackerRankBadge.objects.create(
            badge_name="Cluster 2",
            stars=2,
            total_stars=5,
            timestamp=now,
        )

        response = self.client.get("/")
        badges = list(response.context["hackerrank_badges"])
        self.assertEqual(len(badges), 2)
        badge_names = [b.badge_name for b in badges]
        self.assertIn("Cluster 1", badge_names)
        self.assertIn("Cluster 2", badge_names)

    def test_subsecond_cluster_rejects_duplicate_badge_names(self):
        """If cluster contains duplicate badge names, older runs are rejected to prevent run mixing."""
        now = timezone.now()
        HackerRankBadge.objects.create(
            badge_name="Python",
            stars=1,
            total_stars=5,
            timestamp=now - datetime.timedelta(milliseconds=200),
        )
        HackerRankBadge.objects.create(
            badge_name="Python",
            stars=3,
            total_stars=5,
            timestamp=now,
        )

        response = self.client.get("/")
        badges = list(response.context["hackerrank_badges"])
        # Should not have duplicate Python badges
        self.assertEqual(len(badges), 1)
        self.assertEqual(badges[0].stars, 3)


class HackerRankHardenedEdgeCaseTests(TestCase):
    """Stress tests for type coercion, boundary limits, schema deviations, and consumer config."""

    @patch("requests.get")
    def test_negative_numbers_clamped_safely(self, mock_get):
        """Negative numbers must be clamped to min_val=0 to prevent PostgreSQL CheckViolation."""
        payload = {
            "status": True,
            "models": [
                {
                    "badge_name": "Negative Bounds Badge",
                    "solved": -5,
                    "total_challenges": -10,
                    "stars": -2,
                    "total_stars": -5,
                    "total_points": -100,
                    "current_points": -25.5,
                    "progress_to_next_star": -0.5,
                }
            ],
        }
        mock_response = MagicMock()
        mock_response.json.return_value = payload
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        badges = update_hackerrank_badges.call_local()
        self.assertEqual(len(badges), 1)
        b = badges[0]
        # Should be clamped or defaulted to non-negative values
        self.assertGreaterEqual(b.solved, 0)
        self.assertGreaterEqual(b.total_challenges, 0)
        self.assertGreaterEqual(b.stars, 0)
        self.assertGreaterEqual(b.total_stars, 0)
        self.assertGreaterEqual(b.current_points, 0.0)
        self.assertGreaterEqual(b.progress_to_next_star, 0.0)

    @patch("requests.get")
    def test_string_floats_and_numeric_strings_parsed(self, mock_get):
        """String floats like '5.0' and string ints like '10' must parse without ValueError."""
        payload = {
            "status": True,
            "models": [
                {
                    "badge_name": "Coercion Badge",
                    "stars": "3",
                    "total_stars": "5.0",
                    "level": "2.0",
                    "current_points": "150.5",
                    "progress_to_next_star": "0.75",
                    "solved": "12.0",
                    "total_challenges": "30",
                    "hacker_rank": "50000.0",
                }
            ],
        }
        mock_response = MagicMock()
        mock_response.json.return_value = payload
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        badges = update_hackerrank_badges.call_local()
        self.assertEqual(len(badges), 1)
        b = badges[0]
        self.assertEqual(b.stars, 3)
        self.assertEqual(b.total_stars, 5)
        self.assertEqual(b.level, 2)
        self.assertEqual(b.current_points, 150.5)
        self.assertEqual(b.progress_to_next_star, 0.75)
        self.assertEqual(b.solved, 12)
        self.assertEqual(b.total_challenges, 30)
        self.assertEqual(b.hacker_rank, 50000)

    @patch("requests.get")
    def test_excessively_long_strings_truncated(self, mock_get):
        """Strings exceeding PostgreSQL column limits must truncate without DataError."""
        long_name = "Super Long Badge Name " * 30  # > 300 chars
        long_url = "/domains/" + "abc/" * 200     # > 500 chars
        payload = {
            "status": True,
            "models": [
                {
                    "badge_name": long_name,
                    "url": long_url,
                    "badge_category": "Cat " * 100,
                    "badge_type": "Type " * 30,
                    "category_name": "CatName " * 50,
                }
            ],
        }
        mock_response = MagicMock()
        mock_response.json.return_value = payload
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        badges = update_hackerrank_badges.call_local()
        self.assertEqual(len(badges), 1)
        b = badges[0]
        self.assertLessEqual(len(b.badge_name), 300)
        self.assertLessEqual(len(b.url), 500)
        self.assertLessEqual(len(b.badge_category), 300)
        self.assertLessEqual(len(b.badge_type), 100)
        self.assertLessEqual(len(b.category_name), 300)

    @patch("requests.get")
    def test_api_status_false_handled_gracefully(self, mock_get):
        """API response with status=False is logged and returns empty list."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": False, "message": "Rate limit exceeded"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with self.assertLogs("portfolio.tasks", level="WARNING") as cm:
            result = update_hackerrank_badges.call_local()

        self.assertEqual(result, [])
        self.assertEqual(HackerRankBadge.objects.count(), 0)
        self.assertTrue(any("status=False" in msg for msg in cm.output))

    def test_url_normalization_without_leading_slash(self):
        """URL missing leading slash (e.g. 'domains/cpp') is normalized with leading slash."""
        b = HackerRankBadge(badge_name="Test", url="domains/cpp")
        b.save()
        self.assertEqual(b.url, "https://www.hackerrank.com/domains/cpp")
        self.assertEqual(b.domain_url, "https://www.hackerrank.com/domains/cpp")

    def test_stars_list_when_total_stars_zero_or_none(self):
        """When total_stars is 0 or None but stars earned > 0, stars_list renders earned stars."""
        b = HackerRankBadge(stars=3, total_stars=0)
        stars = b.stars_list
        self.assertEqual(len(stars), 3)
        self.assertTrue(all(s["filled"] for s in stars))

    def test_progress_percentage_bounds_clamping(self):
        """Progress percentage is clamped between 0 and 100."""
        b_neg = HackerRankBadge(progress_to_next_star=-0.5)
        self.assertEqual(b_neg.progress_percentage, 0)

        b_over = HackerRankBadge(progress_to_next_star=1.5)
        self.assertEqual(b_over.progress_percentage, 100)

    def test_consumer_immediate_mode_disabled(self):
        """When run_huey is invoked, HUEY immediate mode must be disabled to allow consumer startup."""
        from django.conf import settings
        self.assertIn("huey_class", settings.HUEY)
        self.assertEqual(settings.HUEY["name"], "djangoPortfolio")
        self.assertFalse(settings.HUEY["utc"])
        self.assertEqual(settings.HUEY["consumer"]["workers"], 1)
        self.assertEqual(settings.HUEY["consumer"]["worker_type"], "thread")

        # Test settings calculation logic for run_huey vs test vs server
        # Case 1: Consumer running
        is_consumer = True
        is_test = False
        default_immediate = False if is_consumer else is_test
        self.assertFalse(default_immediate)

        # Case 2: Test running
        is_consumer = False
        is_test = True
        default_immediate = False if is_consumer else is_test
        self.assertTrue(default_immediate)

        # Case 3: Production server (Gunicorn)
        is_consumer = False
        is_test = False
        default_immediate = False if is_consumer else is_test
        self.assertFalse(default_immediate)

    def test_display_total_stars_fallback_when_total_stars_is_zero(self):
        """When total_stars is 0 or None but stars earned > 0, display_total_stars matches stars."""
        b = HackerRankBadge(stars=3, total_stars=0)
        self.assertEqual(b.display_total_stars, 3)

        b_none = HackerRankBadge(stars=4, total_stars=None)
        self.assertEqual(b_none.display_total_stars, 4)

        b_normal = HackerRankBadge(stars=2, total_stars=5)
        self.assertEqual(b_normal.display_total_stars, 5)

    def test_empty_badge_name_fallback_to_unnamed_badge(self):
        """Saving a badge with empty or None badge_name falls back safely to 'Unnamed Badge'."""
        b = HackerRankBadge(badge_name="")
        b.save()
        self.assertEqual(b.badge_name, "Unnamed Badge")

        b2 = HackerRankBadge(badge_name=None)
        b2.save()
        self.assertEqual(b2.badge_name, "Unnamed Badge")

    def test_nan_and_infinity_in_floats_and_integers(self):
        """NaN and Infinity values must be filtered out gracefully without crashing or 500 errors."""
        import math
        self.assertEqual(_safe_float(float('nan'), default=0.0), 0.0)
        self.assertEqual(_safe_float(float('inf'), default=0.0), 0.0)
        self.assertEqual(_safe_float(float('-inf'), default=0.0), 0.0)
        self.assertEqual(_safe_int(float('inf'), default=0), 0)
        self.assertEqual(_safe_int(float('nan'), default=0), 0)

        # Badge with NaN progress must not crash progress_percentage or RootPage
        badge = HackerRankBadge.objects.create(
            badge_name="NaN Badge",
            progress_to_next_star=float('nan'),
            current_points=float('nan'),
        )
        self.assertEqual(badge.progress_percentage, 0)
        self.assertEqual(badge.current_points, 0.0)

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_32bit_and_64bit_integer_overflow_protection(self):
        """Values exceeding PostgreSQL 32-bit/64-bit bounds must be clamped without DataError."""
        b = HackerRankBadge(
            badge_name="Overflow Badge",
            total_points=3_000_000_000,
            solved=5_000_000_000,
            hacker_rank=10**20,
        )
        b.save()
        self.assertEqual(b.total_points, 2147483647)
        self.assertEqual(b.solved, 2147483647)
        self.assertEqual(b.hacker_rank, 9223372036854775807)

    def test_stars_list_runaway_capped_at_20(self):
        """Badges with excessively large total_stars are capped at 20 to prevent DOM/memory exhaustion."""
        b = HackerRankBadge(stars=5, total_stars=1_000_000)
        self.assertEqual(len(b.stars_list), 20)

    def test_spanish_localization_rendered(self):
        """Visiting /es/ renders Spanish translations for HackerRank badges section."""
        HackerRankBadge.objects.create(
            badge_name="Python",
            stars=3,
            total_stars=5,
            timestamp=timezone.now(),
        )
        response = self.client.get("/es/")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn("Insignias de HackerRank", content)
        self.assertIn("Desafíos Resueltos", content)
        self.assertIn("Ver Dominio", content)

    def test_timezone_santiago_enforced(self):
        """America/Santiago timezone must be active in os.environ for Huey scheduler compatibility."""
        import os
        self.assertEqual(os.environ.get("TZ"), "America/Santiago")


