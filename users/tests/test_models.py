from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating user with email"""
        email = "test@example.com"
        password = "password123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)

    def test_new_user_invalid_email(self):
        """Test creating user with invalid email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "password123")

    def test_create_superuser(self):
        """Test create superuser"""
        user = get_user_model().objects.create_superuser(
            "admin@example.com", "password123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
