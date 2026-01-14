from django.utils import timezone
from rest_framework import serializers
from library.models import Borrowing, Book


class BookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")


class BorrowingReadSerializer(serializers.ModelSerializer):
    book = BookDetailSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )
        
        
class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "book", "expected_return_date")
        read_only_fields = ("id",)

    def validate_expected_return_date(self, value):
        today = timezone.localdate()
        if value < today:
            raise serializers.ValidationError("Expected return date cannot be "
                                              "earlier than today.")
        return value
