import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from tickets.models import Subject
from .models import Material


class MaterialAccessTests(TestCase):
    def setUp(self):
        self._media = tempfile.TemporaryDirectory()
        self.addCleanup(self._media.cleanup)
        media_settings = override_settings(MEDIA_ROOT=self._media.name)
        media_settings.enable()
        self.addCleanup(media_settings.disable)
        self.user = get_user_model().objects.create_user(username="student", password="test-Pass-123")
        self.subject = Subject.objects.create(name="Математика")
        self.material = Material.objects.create(
            title="Конспект", subject=self.subject, teacher="Иванов", course=1, year=2026,
            file=SimpleUploadedFile("lecture.pdf", b"%PDF-1.4\nhello"),
        )
        self.archive = reverse("materials:index")
        self.file_url = reverse("materials:download", args=[self.material.pk])

    def test_archive_and_file_require_login(self):
        for url in (self.archive, self.file_url, reverse("materials:upload")):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/accounts/login/?next=", response.url)
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)
        self.assertEqual(self.client.get(reverse("accounts:login")).status_code, 200)
        self.assertEqual(self.client.get("/media/materials/lecture.pdf").status_code, 404)

    def test_successful_login_returns_to_original_page(self):
        response = self.client.post(
            reverse("accounts:login") + f"?next={self.archive}",
            {"username": "student", "password": "test-Pass-123"},
        )
        self.assertRedirects(response, self.archive)

    def test_hidden_is_not_public_and_can_be_restored(self):
        self.client.force_login(self.user)
        self.material.is_hidden = True
        self.material.save()
        self.assertNotContains(self.client.get(self.archive), "Конспект")
        self.assertEqual(self.client.get(self.file_url).status_code, 404)
        self.material.is_hidden = False
        self.material.save()
        self.assertContains(self.client.get(self.archive), "Конспект")
        self.assertEqual(self.client.get(self.file_url).status_code, 200)

    def test_filters_are_combined_and_preserved_in_url(self):
        Material.objects.create(
            title="Лекция 2", subject=self.subject, teacher="Петров", course=2, year=2025,
            file=SimpleUploadedFile("two.pdf", b"%PDF-1.4\nhello"),
        )
        self.client.force_login(self.user)
        response = self.client.get(self.archive, {"subject": self.subject.pk, "teacher": "Иванов", "course": "1", "year": "2026"})
        self.assertContains(response, "Конспект")
        self.assertNotContains(response, "Лекция 2")
        self.assertContains(response, 'name="year"')
        self.assertContains(self.client.get(self.archive, {"course": "6"}), "Ничего не найдено")

    def test_file_size_limit_keeps_other_fields(self):
        self.client.force_login(self.user)
        large = SimpleUploadedFile("large.pdf", b"%PDF" + b"a" * (20 * 1024 * 1024 + 1))
        response = self.client.post(reverse("materials:upload"), {
            "title": "Большой конспект", "subject": self.subject.pk, "teacher": "Профессор",
            "course": 1, "year": 2026, "file": large,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "20 МБ")
        self.assertContains(response, "Большой конспект")
        self.assertFalse(Material.objects.filter(title="Большой конспект").exists())

    def test_file_under_limit_is_uploaded(self):
        self.client.force_login(self.user)
        normal = SimpleUploadedFile("normal.pdf", b"%PDF" + b"a" * (19 * 1024 * 1024))
        response = self.client.post(reverse("materials:upload"), {
            "title": "Новый конспект", "subject": self.subject.pk, "teacher": "Профессор",
            "course": 1, "year": 2026, "file": normal,
        })
        self.assertRedirects(response, self.archive)
        self.assertTrue(Material.objects.filter(title="Новый конспект").exists())


class FavoriteTests(TestCase):
    def setUp(self):
        from .models import MaterialFavorite
        self.user = get_user_model().objects.create_user(username='favorite_student',password='test-password-123')
        subject = Subject.objects.create(name='Физика')
        self.media_temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.media_temp.cleanup)
        override = override_settings(MEDIA_ROOT=self.media_temp.name)
        override.enable()
        self.addCleanup(override.disable)
        self.material = Material.objects.create(title='Избранная лекция',subject=subject,teacher='Смирнов',course=1,year=2026,file=SimpleUploadedFile('test.pdf', b'%PDF-1.4\nhello'))
        self.url = reverse('materials:toggle_favorite',args=[self.material.pk])
        self.client.force_login(self.user)

    def test_favorite_is_saved(self):
        from .models import MaterialFavorite
        result = self.client.post(self.url, data='{"favorite":true}',content_type='application/json')
        self.assertEqual(result.status_code,200)
        self.assertTrue(MaterialFavorite.objects.filter(user=self.user,material=self.material).exists())
        self.assertContains(self.client.get(reverse('materials:index')), '★')

    def test_hidden_material_cannot_be_favorited(self):
        self.material.is_hidden=True
        self.material.save()
        self.assertEqual(self.client.post(self.url,data='{"favorite":true}',content_type='application/json').status_code,404)
