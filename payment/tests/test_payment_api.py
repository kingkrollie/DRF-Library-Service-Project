from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from library.models import Book, Borrowing
from payment.models import Payment
from payment.services import create_payment_session
from payment.views import StripeWebhookView

PAYMENTS_URL = reverse("payment:payments-list")
user = get_user_model()


def get_jwt_token(client, user):
    res = client.post(
        reverse("users:token_obtain_pair"),
        {
            "email": user.email,
            "password": "testpass123",
        },
    )
    return res.data["access"]


class PaymentViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user1 = user.objects.create_user(
            email="user1@test.com", password="testpass123"
        )
        self.user2 = user.objects.create_user(
            email="user2@test.com", password="testpass123"
        )

        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            inventory=10,
            daily_fee=5
        )

        borrow_date = date.today()
        expected_return_date = borrow_date + timedelta(days=7)

        self.borrowing1 = Borrowing.objects.create(
            user=self.user1,
            book=self.book,
            borrow_date=borrow_date,
            expected_return_date=expected_return_date,
        )
        self.borrowing2 = Borrowing.objects.create(
            user=self.user2,
            book=self.book,
            borrow_date=borrow_date,
            expected_return_date=expected_return_date,
        )

        self.payment1 = Payment.objects.create(
            borrowing=self.borrowing1,
            session_id="sess_1",
            session_url="http://example.com/1",
            money=100,
            status=Payment.Status.PENDING,
            type=Payment.Type.PAYMENT,
        )
        self.payment2 = Payment.objects.create(
            borrowing=self.borrowing2,
            session_id="sess_2",
            session_url="http://example.com/2",
            money=200,
            status=Payment.Status.PENDING,
            type=Payment.Type.PAYMENT,
        )

    def test_user_sees_only_own_payments(self):
        token = get_jwt_token(self.client, self.user1)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        res = self.client.get(PAYMENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        results = res.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.payment1.id)

    def test_unauthenticated_user_cannot_see_payments(self):
        self.client.credentials()

        res = self.client.get(PAYMENTS_URL)

        self.assertEqual(res.status_code, 401)


class PaymentSessionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user1 = user.objects.create_user(
            email="user1@test.com", password="testpass123"
        )

        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            inventory=10,
            daily_fee=5
        )
        self.days = 6

        borrow_date = date.today()
        expected_return_date = borrow_date + timedelta(days=self.days)

        self.borrowing = Borrowing.objects.create(
            user=self.user1,
            book=self.book,
            borrow_date=borrow_date,
            expected_return_date=expected_return_date,
        )

        self.exp_borrowing = Borrowing.objects.create(
            user=self.user1,
            book=self.book,
            borrow_date=date.today(),
            expected_return_date=date.today() + timedelta(days=5),
            actual_return_date=date.today() + timedelta(days=10)
        )

    def test_correct_total_price(self):
        session = create_payment_session(self.borrowing)
        price = session.total_price / 100
        calculate_total = (self.days * self.book.daily_fee)
        self.assertEqual(price, calculate_total)

    def test_correct_fee_price(self):
        session = create_payment_session(self.exp_borrowing)
        price = session.total_price / 100
        days = (
                self.exp_borrowing.actual_return_date - self.exp_borrowing.expected_return_date).days
        calculate_total = days * self.book.daily_fee
        self.assertEqual(price, calculate_total)
