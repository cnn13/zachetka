from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Subject, Ticket, TicketProgress


class RandomTicketTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="student", password="test-Pass-123")
        self.subject = Subject.objects.create(name="Алгебра")
        self.weak = Ticket.objects.create(subject=self.subject, number=1, text="Сложный вопрос")
        self.learned = Ticket.objects.create(subject=self.subject, number=2, text="Изученный вопрос")
        self.client.force_login(self.user)

    def test_weak_ticket_first_and_progress_persists(self):
        TicketProgress.objects.create(user=self.user, ticket=self.learned, status=TicketProgress.LEARNED)
        for _ in range(10):
            response = self.client.get(reverse("tickets:random"))
            self.assertContains(response, "Сложный вопрос")
            self.assertNotContains(response, "Изученный вопрос")
        self.client.post(reverse("tickets:set_status", args=[self.weak.pk]), {"status": "bad"})
        self.assertEqual(TicketProgress.objects.get(user=self.user, ticket=self.weak).status, TicketProgress.BAD)
        self.assertContains(self.client.get(reverse("tickets:random")), "Сложный вопрос")

    def test_learned_fallback_when_all_learned(self):
        for ticket in [self.weak, self.learned]:
            TicketProgress.objects.create(user=self.user, ticket=ticket, status=TicketProgress.LEARNED)
        self.assertEqual(self.client.get(reverse("tickets:random")).status_code, 200)

    def test_invalid_status_does_not_modify_progress(self):
        response = self.client.post(reverse("tickets:set_status", args=[self.weak.pk]), {"status": "wrong"})
        self.assertEqual(response.status_code, 404)
        self.assertFalse(TicketProgress.objects.exists())

    def test_progress_is_per_user(self):
        self.client.post(reverse("tickets:set_status", args=[self.weak.pk]), {"status": "learned"})
        other = get_user_model().objects.create_user(username="other", password="password123")
        self.client.force_login(other)
        self.assertEqual(TicketProgress.objects.filter(user=other).count(), 0)
