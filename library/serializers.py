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
