from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


UPDATE_USER = reverse("users:manage")


class UserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "email": "test@example.com",
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe",
        }
        self.user = get_user_model().objects.create_user(**self.user_data)

        self.client.force_authenticate(user=self.user)

    def test_get_user_data(self):
        """Test retrieve user data"""
        res = self.client.get(UPDATE_USER)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.user.email)
        self.assertEqual(res.data["first_name"], self.user.first_name)
        self.assertNotIn("password", res.data)

    def test_update_user(self):
        """Test update user profile data (PUT)"""
        payload = {
            "first_name": "NewName",
            "last_name": "NewLastName",
            "password": "newpassword123",
            "email": self.user.email,
        }

        res = self.client.put(UPDATE_USER, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.first_name, payload["first_name"])
        self.assertTrue(self.user.check_password(payload["password"]))

    def test_partial_update_user(self):
        """Test update user profile data (PATCH)"""
        payload = {
            "first_name": "Nick",
        }

        res = self.client.patch(UPDATE_USER, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.first_name, payload["first_name"])
