from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from library.models import Book
from library.serializers import BookSerializer


BOOK_URL = reverse("book-list")


def detail_url(book_id):
    return reverse("book-detail", args=[book_id])


def sample_book(**params):
    defaults = {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "cover": Book.Cover.HARD,
        "inventory": 5,
        "daily_fee": "1.50",
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


class UnauthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_books_allowed(self):
        sample_book()
        sample_book(title="Refactoring")

        res = self.client.get(BOOK_URL)

        books = Book.objects.order_by("id")
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_book_allowed(self):
        book = sample_book()

        res = self.client.get(detail_url(book.id))

        serializer = BookSerializer(book)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_book_forbidden(self):
        payload = {
            "title": "DDD",
            "author": "Eric Evans",
            "cover": Book.Cover.HARD,
            "inventory": 3,
            "daily_fee": "2.00",
        }

        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AuthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_books_allowed(self):
        sample_book()
        sample_book(title="Design Patterns")

        res = self.client.get(BOOK_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_book_forbidden(self):
        payload = {
            "title": "DDD",
            "author": "Eric Evans",
            "cover": Book.Cover.SOFT,
            "inventory": 2,
            "daily_fee": "2.50",
        }

        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_forbidden(self):
        book = sample_book()

        res = self.client.patch(
            detail_url(book.id),
            {"inventory": 10},
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_forbidden(self):
        book = sample_book()

        res = self.client.delete(detail_url(book.id))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_user(
            email="admin@test.com",
            password="adminpass",
            is_staff=True,
        )
        self.client.force_authenticate(self.admin)

    def test_create_book_success(self):
        payload = {
            "title": "Domain-Driven Design",
            "author": "Eric Evans",
            "cover": Book.Cover.HARD,
            "inventory": 4,
            "daily_fee": "3.00",
        }

        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=res.data["id"])

        for key in payload:
            self.assertEqual(str(payload[key]), str(getattr(book, key)))

    def test_update_book_success(self):
        book = sample_book()

        payload = {"inventory": 10}

        res = self.client.patch(detail_url(book.id), payload)

        book.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(book.inventory, 10)

    def test_delete_book_success(self):
        book = sample_book()

        res = self.client.delete(detail_url(book.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=book.id).exists())
