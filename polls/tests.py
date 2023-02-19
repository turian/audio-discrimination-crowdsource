from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestCheckUserLock(APITestCase):
    def setUp(self):
        self.client = Client()
        self.locked_user = get_user_model().objects.create(
            username="test_user", is_locked=True
        )
        self.locked_user.set_password("test_password")
        self.locked_user.save()

        self.user = get_user_model().objects.create(username="test", is_locked=False)
        self.user.set_password("test_password")
        self.user.save()

    def test_check_user_lock(self):
        url = reverse("task-flow")
        expected_url = reverse("thank-you")
        self.client.login(username=self.locked_user.username, password="test_password")
        response = self.client.get(url)
        self.assertTrue(self.locked_user.is_locked)
        self.assertRedirects(response, expected_url)
        self.assertTemplateUsed("polls/thanks.html")

    def test_check_user_lock_no_redirect(self):
        url = reverse("task-flow")
        self.client.login(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertTemplateUsed("polls/task_flow.html")
