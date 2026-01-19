from django.contrib.auth import get_user_model
from django.test import TestCase
from users.serializers import UserSerializer


class SerializerTests(TestCase):
    def test_user_serializer(self):
        """Test user serializer validation """
        payload = {
            "email": "test@example.com",
            "password": "VeryLongPassword",
        }
        serializer = UserSerializer(data=payload)

        self.assertTrue(serializer.is_valid())

    def test_user_serializer_validation(self):
        """Test user serializer validation """
        payload = {
            "email": "test@example.com",
            "password": "short",
            "first_name": "John"
        }
        serializer = UserSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_user_serializer_update(self):
        """Test user serializer update"""
        user = get_user_model().objects.create_user("old@ex.com", "pass123")
        payload = {"first_name": "NewName", "password": "newpassword123"}

        serializer = UserSerializer(instance=user, data=payload, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user.refresh_from_db()
        self.assertEqual(user.first_name, "NewName")
        self.assertTrue(user.check_password("newpassword123"))
