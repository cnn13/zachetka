import json
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import PomodoroSession


class PomodoroSessionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="student", password="examplePassword123")
        self.url = reverse("timer:save_session")
        self.client.force_login(self.user)

    def test_save_and_show_completed_session(self):
        payload = {"subject_name": "Математика", "duration_minutes": 25, "token": "sample-client-token-1234"}
        first = self.client.post(self.url, json.dumps(payload), content_type="application/json")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(PomodoroSession.objects.count(), 1)
        # Повторный fetch не удваивает статистику.
        again = self.client.post(self.url, json.dumps(payload), content_type="application/json")
        self.assertEqual(again.status_code, 200)
        self.assertEqual(PomodoroSession.objects.count(), 1)
        self.assertContains(self.client.get(reverse("timer:sessions")), "Математика")
        self.assertContains(self.client.get(reverse("timer:index")), "Математика")

    def test_other_user_cannot_view_sessions(self):
        PomodoroSession.objects.create(user=self.user, subject_name="Личный предмет", duration_minutes=25, client_token="private-client-token-1234")
        other = get_user_model().objects.create_user(username="other", password="examplePassword123")
        self.client.force_login(other)
        self.assertNotContains(self.client.get(reverse("timer:sessions")), "Личный предмет")

    def test_unauthenticated_cannot_save_or_view(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse("timer:index")).status_code, 302)
        self.assertEqual(self.client.get(reverse("timer:sessions")).status_code, 302)
        self.assertEqual(self.client.post(self.url, "{}", content_type="application/json").status_code, 302)

    def test_rejects_incomplete_session(self):
        response = self.client.post(self.url, json.dumps({"subject_name": "Математика", "duration_minutes": 1, "token": "test-invalid-session-1234"}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(PomodoroSession.objects.exists())
