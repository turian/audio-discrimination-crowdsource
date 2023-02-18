from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestCheckUserLock(APITestCase):
    """This class set up a test case and test if CheckUserLockMixin
    actually redirect to thank you page.
    """

    def setUp(self):
        self.locked_user = get_user_model().objects.create(
            username="test_user", password="test_password", is_locked=True
        )
        self.user = get_user_model().objects.create(
            username="test", password="test_password"
        )

    def test_check_user_lock(self):
        url = reverse("auth-flow")
        expected_url = reverse("thank-you")
        self.client.force_authenticate(user=self.locked_user)
        response = self.client.get(url)
        self.assertRedirects(response, expected_url)
        self.assertTemplateUsed("polls/thanks.html")

    def test_check_user_lock_no_redirect(self):
        url = reverse("task-flow")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertTemplateUsed("polls/task_flow.html")
