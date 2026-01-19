from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model

from library.models import Book, Borrowing


class BorrowingNotificationAPITests(TestCase):
    def test_notify_task_called_on_borrowing_create(self):
        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="password123"
        )

        book = Book.objects.create(
            title="Test Book",
            author="Author",
            inventory=5,
            daily_fee=10
        )

        client = APIClient()
        client.force_authenticate(user=user)

        payload = {
            "book": book.id,
            "expected_return_date": "2030-01-20"
        }

        with patch("notifications.tasks.notify_new_borrowing.delay") as mocked_task: # noqa
            response = client.post(
                reverse("library:borrowing-list"),
                payload
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Borrowing.objects.count(), 1)
        mocked_task.assert_called_once()
