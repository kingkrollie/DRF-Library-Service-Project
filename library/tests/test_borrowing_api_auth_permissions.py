from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from library.models import Book, Borrowing


BORROWING_LIST_CREATE = reverse("library:borrowing-list")


def borrowing_detail_url(borrowing_id: int) -> str:
    return reverse("library:borrowing-detail", args=[borrowing_id])


def get_results(data):
    return data["results"] if isinstance(data, dict) and "results" in data else data # noqa


class BorrowingAuthPermissionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user1@test.com",
            password="password123",
        )
        self.user2 = get_user_model().objects.create_user(
            email="user2@test.com",
            password="password123",
        )
        self.admin = get_user_model().objects.create_superuser(
            "admin@test.com",
            "password123",
        )

        self.book = Book.objects.create(
            title="Book A",
            author="Author A",
            cover=Book.Cover.HARD,
            inventory=5,
            daily_fee="1.50",
        )

    def _create_borrowing(self, user, returned=False):
        expected = timezone.localdate() + timedelta(days=7)
        borrowing = Borrowing.objects.create(
            user=user,
            book=self.book,
            expected_return_date=expected,
        )
        if returned:
            borrowing.actual_return_date = timezone.localdate()
            borrowing.save(update_fields=["actual_return_date"])
        return borrowing

    # ---- Auth ----

    def test_list_requires_auth(self):
        res = self.client.get(BORROWING_LIST_CREATE)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_requires_auth(self):
        borrowing = self._create_borrowing(self.user)
        res = self.client.get(borrowing_detail_url(borrowing.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---- Permissions (owner/staff) ----

    def test_non_admin_sees_only_own_borrowings(self):
        own = self._create_borrowing(self.user)
        self._create_borrowing(self.user2)

        self.client.force_authenticate(user=self.user)
        res = self.client.get(BORROWING_LIST_CREATE)

        results = get_results(res.data)
        ids = [item["id"] for item in results]

        self.assertIn(own.id, ids)
        self.assertEqual(len(ids), 1)

    def test_owner_can_retrieve_detail(self):
        borrowing = self._create_borrowing(self.user)

        self.client.force_authenticate(user=self.user)
        res = self.client.get(borrowing_detail_url(borrowing.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], borrowing.id)
        self.assertIn("book", res.data)
        self.assertEqual(res.data["book"]["id"], self.book.id)

    def test_non_owner_cannot_retrieve_detail(self):
        borrowing = self._create_borrowing(self.user)

        self.client.force_authenticate(user=self.user2)
        res = self.client.get(borrowing_detail_url(borrowing.id))

        self.assertIn(
            res.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND],
        )

    def test_admin_can_retrieve_detail_for_other_user(self):
        borrowing = self._create_borrowing(self.user)

        self.client.force_authenticate(user=self.admin)
        res = self.client.get(borrowing_detail_url(borrowing.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], borrowing.id)

    def test_admin_list_sees_all_borrowings(self):
        b1 = self._create_borrowing(self.user)
        b2 = self._create_borrowing(self.user2)

        self.client.force_authenticate(user=self.admin)
        res = self.client.get(BORROWING_LIST_CREATE)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        results = get_results(res.data)
        ids = [item["id"] for item in results]

        self.assertIn(b1.id, ids)
        self.assertIn(b2.id, ids)
