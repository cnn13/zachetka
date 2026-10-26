import json
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Profile, StudyGroup

class ProfileUpdateTests(TestCase):
    def test_group_changes_persist(self):
        user = get_user_model().objects.create_user(username='student', password='examplePassword123')
        first = StudyGroup.objects.create(name='8Б41')
        second = StudyGroup.objects.create(name='8Б42')
        Profile.objects.create(user=user, group=first)
        self.client.force_login(user)
        response = self.client.post(reverse('accounts:update_profile'),json.dumps({'group':second.name}), content_type='application/json')
        self.assertEqual(response.status_code,200)
        self.assertEqual(Profile.objects.get(user=user).group,second)
        self.assertContains(self.client.get(reverse('accounts:index')), '8Б42')
