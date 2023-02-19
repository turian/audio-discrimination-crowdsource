from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Annotation, Batch, Task


class LockUserAnnotationListTest(APITestCase):
    """This class sets up the test db and tests
    - 'lock-users-api' endpoint
    - 'annotation-api' endpoint
    """

    def setUp(self):
        self.user = get_user_model().objects.create(
            username="test_user", password="testpass"
        )
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
            user=self.user,
            task=self.task_1,
            annotated_at=timezone.now(),
            task_presentation="AAB",
            annotations="XXY",
        )

    def test_lock_user(self):
        url = reverse("lock-users-api")
        self.client.force_authenticate(user=self.admin_user)
        payload = {"users": [self.user.id, 5, 10]}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"users_not_found": [5, 10]})

    def test_annotation_list(self):
        url = reverse("annotation-api")
        expected_output = [
            {
                "id": 1,
                "user": 1,
                "task": 1,
                "annotated_at": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                "task_presentation": "AAB",
                "annotations": "XXY",
            }
        ]
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_output)
