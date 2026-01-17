from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from library.models import Book, Borrowing


BORROWING_LIST_CREATE = reverse("library:borrowing-list")


def borrowing_return_url(borrowing_id: int) -> str:
    return reverse("library:borrowing-return-book", args=[borrowing_id])


class BorrowingCreateReturnTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user1@test.com",
            password="password123",
        )

        self.book_a = Book.objects.create(
            title="Book A",
            author="Author A",
            cover=Book.Cover.HARD,
            inventory=2,
            daily_fee="1.50",
        )
        self.book_b = Book.objects.create(
            title="Book B",
            author="Author B",
            cover=Book.Cover.SOFT,
            inventory=1,
            daily_fee="2.00",
        )

    def _payload(self, book_id: int):
        return {
            "book": book_id,
            "expected_return_date": (
                        timezone.localdate() + timedelta(days=7)).isoformat(),
        }

    # ---- Auth ----

    def test_borrowing_list_requires_auth(self):
        res = self.client.get(BORROWING_LIST_CREATE)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_borrowing_requires_auth(self):
        res = self.client.post(BORROWING_LIST_CREATE,
                               self._payload(self.book_b.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---- Create borrowing ----

    def test_create_borrowing_decreases_inventory_and_attaches_user(self):
        self.client.force_authenticate(user=self.user)

        res = self.client.post(BORROWING_LIST_CREATE,
                               self._payload(self.book_b.id))

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", res.data)

        borrowing = Borrowing.objects.get(id=res.data["id"])
        self.assertEqual(borrowing.user_id, self.user.id)
        self.assertEqual(borrowing.book_id, self.book_b.id)

        self.book_b.refresh_from_db()
        self.assertEqual(self.book_b.inventory, 0)

    def test_create_borrowing_out_of_stock_returns_400(self):
        self.book_b.inventory = 0
        self.book_b.save(update_fields=["inventory"])

        self.client.force_authenticate(user=self.user)

        res = self.client.post(BORROWING_LIST_CREATE,
                               self._payload(self.book_b.id))

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("book", res.data)

    # ---- Return borrowing ----

    def test_return_borrowing_sets_actual_return_date_and_increases_inventory(self):
        self.client.force_authenticate(user=self.user)

        res_create = self.client.post(BORROWING_LIST_CREATE,
                                      self._payload(self.book_a.id))
        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)

        self.book_a.refresh_from_db()
        self.assertEqual(self.book_a.inventory, 1)

        borrowing_id = res_create.data["id"]

        res_return = self.client.post(borrowing_return_url(borrowing_id))
        self.assertEqual(res_return.status_code, status.HTTP_200_OK)

        borrowing = Borrowing.objects.get(id=borrowing_id)
        self.assertEqual(borrowing.actual_return_date, timezone.localdate())

        self.book_a.refresh_from_db()
        self.assertEqual(self.book_a.inventory, 2)

    def test_return_borrowing_twice_returns_400(self):
        self.client.force_authenticate(user=self.user)

        res_create = self.client.post(BORROWING_LIST_CREATE,
                                      self._payload(self.book_a.id))
        borrowing_id = res_create.data["id"]

        res1 = self.client.post(borrowing_return_url(borrowing_id))
        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        res2 = self.client.post(borrowing_return_url(borrowing_id))
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res2.data["detail"],
                         "This borrowing is already returned.")
