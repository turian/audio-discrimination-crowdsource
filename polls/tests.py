from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Annotation, AnnotatorProfile, Batch, Task


class TestCheckUserLock(APITestCase):
    """This class set up a test case and test if CheckUserLockMixin
    actually redirect user to thank you page if user is locked and
    it also assert that unlocked users have access to their desired page.
    """

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


class LockUserAnnotationListTest(APITestCase):
    """This class sets up the test db and tests
    - 'lock-users-api' endpoint
    - 'annotation-api' endpoint
    """

    def setUp(self):
        self.user = get_user_model().objects.create(
            username="test_user", password="testpass"
        )
        self.annotator = AnnotatorProfile.objects.create(annotator=self.user)
        self.admin_user = get_user_model().objects.create(
            username="test_admin", password="testpass", is_staff=True
        )
        self.batch = Batch.objects.create(created_at=timezone.now(), notes="test note")
        self.task_1 = Task.objects.create(
            batch=self.batch,
            reference_url="http://www.test.com",
            transform_url="http://www.example.com",
            transform_metadata={"test": 1},
        )
        self.annotatation = Annotation.objects.create(
            user=self.annotator,
            task=self.task_1,
            annotated_at=timezone.now(),
            task_presentation="AAB",
            annotations="XXY",
        )

    def test_lock_user(self):
        url = reverse("lock-users-api")
        self.client.force_authenticate(user=self.admin_user)
        payload = {"users": [self.user.id, 15, 10]}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"users_not_found": [15, 10]})

    def test_annotation_list(self):
        url = reverse("annotation-api")
        expected_output = [
            {
                "id": 1,
                "user": self.annotator.id,
                "task": self.task_1.id,
                "annotated_at": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                "task_presentation": "AAB",
                "annotations": "XXY",
                "is_correct": False
            }
        ]
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_output)


class BatchTasksAPIViewTest(APITestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create(
            username="test_admin", password="testpass", is_staff=True, is_superuser=True
        )

        self.valid_payload = {
            "is_gold": True,
            "notes": "Test batch",
            "tasks": [
                {
                    "reference_url": "http://example.com/reference",
                    "transform_url": "http://example.com/transform",
                    "transform_metadata": {"foo": "bar"},
                },
                {
                    "reference_url": "http://example.com/reference2",
                    "transform_url": "http://example.com/transform2",
                    "transform_metadata": {"baz": "qux"},
                },
            ],
            "set_to_current_batch_gold": True,
        }

    def create_batch(self):
        """
        Test batch job creation view for expected status code output.
        """
        url = reverse("batch-tasks-api")
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(url, self.valid_payload, format="json", follow=True)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {"status": "success"})

    def test_create_batch_view_on_get(self):
        """This method is not allowed, hence 405 is expected."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse("batch-tasks-api"))
        self.assertEqual(response.status_code, 405)
