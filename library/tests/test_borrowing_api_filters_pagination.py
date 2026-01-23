from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from library.models import Book, Borrowing


BORROWING_LIST = "/api/borrowings/"


class BorrowingFiltersPaginationTests(TestCase):
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

        self.book_a = Book.objects.create(
            title="Book A",
            author="Author A",
            cover=Book.Cover.HARD,
            inventory=500,
            daily_fee="1.50",
        )
        self.book_b = Book.objects.create(
            title="Book B",
            author="Author B",
            cover=Book.Cover.SOFT,
            inventory=500,
            daily_fee="2.00",
        )

    def _create_borrowing(self, user, book, returned=False):
        expected = timezone.localdate() + timedelta(days=7)
        borrowing = Borrowing.objects.create(
            user=user,
            book=book,
            expected_return_date=expected,
        )
        if returned:
            borrowing.actual_return_date = timezone.localdate()
            borrowing.save(update_fields=["actual_return_date"])
        return borrowing

    # ---- Pagination ----

    def test_list_is_paginated(self):
        for _ in range(101):
            self._create_borrowing(self.user, self.book_a)

        self.client.force_authenticate(user=self.user)
        res1 = self.client.get(BORROWING_LIST)

        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertIn("count", res1.data)
        self.assertIn("results", res1.data)
        self.assertIn("next", res1.data)

        self.assertEqual(res1.data["count"], 101)
        self.assertEqual(len(res1.data["results"]), 100)
        self.assertIsNotNone(res1.data["next"])

        res2 = self.client.get(res1.data["next"])
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res2.data["results"]), 1)

    # ---- Filters: is_active ----

    def test_filter_is_active_true(self):
        active = self._create_borrowing(self.user, self.book_a, returned=False)
        returned = self._create_borrowing(
            self.user, self.book_a, returned=True
        )

        self.client.force_authenticate(user=self.user)
        res = self.client.get(BORROWING_LIST, {"is_active": "true"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in res.data["results"]]
        self.assertIn(active.id, ids)
        self.assertNotIn(returned.id, ids)

    def test_filter_is_active_false(self):
        active = self._create_borrowing(self.user, self.book_a, returned=False)
        returned = self._create_borrowing(
            self.user, self.book_a, returned=True
        )

        self.client.force_authenticate(user=self.user)
        res = self.client.get(BORROWING_LIST, {"is_active": "false"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in res.data["results"]]
        self.assertIn(returned.id, ids)
        self.assertNotIn(active.id, ids)

    # ---- Filter: book ----

    def test_filter_book(self):
        b_a = self._create_borrowing(self.user, self.book_a)
        b_b = self._create_borrowing(self.user, self.book_b)

        self.client.force_authenticate(user=self.user)
        res = self.client.get(BORROWING_LIST, {"book": str(self.book_a.id)})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in res.data["results"]]
        self.assertIn(b_a.id, ids)
        self.assertNotIn(b_b.id, ids)

    # ---- Filter: admin user_id ----

    def test_admin_filter_user_id(self):
        b_user = self._create_borrowing(self.user, self.book_a)
        self._create_borrowing(self.user2, self.book_a)

        self.client.force_authenticate(user=self.admin)
        res = self.client.get(BORROWING_LIST, {"user_id": self.user.id})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in res.data["results"]]
        self.assertIn(b_user.id, ids)
        self.assertEqual(len(ids), 1)
