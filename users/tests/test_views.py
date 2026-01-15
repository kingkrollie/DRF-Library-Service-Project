from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status


class ViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("users:manage")
        self.user = get_user_model().objects.create_user("test@ex.com", "pass12345")

    def test_retrieve_user_unauthorized(self):
        """Test anonim retrieve user data (401)"""
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_object_returns_current_user(self):
        """Test get object return current user"""
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.user.email)
