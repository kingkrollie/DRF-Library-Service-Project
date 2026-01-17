from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from library.models import Borrowing, Book
from payment.models import Payment
from payment.services import create_payment_session


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "daily_fee",
        )


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

    def create(self, validated_data):
        request = self.context["request"]
        book = validated_data["book"]

        validated_data.pop('user', None)

        with transaction.atomic():
            borrowing = Borrowing.objects.create(
                user=request.user,
                **validated_data
            )

            book.inventory -= 1
            book.save(update_fields=["inventory"])

            session = create_payment_session(borrowing)

            Payment.objects.create(
                borrowing=borrowing,
                session_id=session.id,
                session_url=session.url,
                money=session.total_price,
                status=Payment.Status.PENDING,
                type=Payment.Type.PAYMENT,
            )

        return borrowing
