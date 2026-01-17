from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from library.models import Book, Borrowing
from notifications.tasks import notify_new_borrowing


class NotifyNewBorrowingTests(TestCase):
    def test_notify_new_borrowing_calls_telegram_helper(self):
        user = get_user_model().objects.create_user(
            email="user@test.com",
            password="password"
        )

        book = Book.objects.create(
            title="Clean Code",
            author="Robert Martin",
            inventory=3,
            daily_fee=1
        )

        borrowing = Borrowing.objects.create(
            user=user,
            book=book,
            expected_return_date="2030-01-20"
        )

        with patch("notifications.tasks.send_telegram_message") as mocked_send:
            notify_new_borrowing(borrowing.id)

        mocked_send.assert_called_once()
