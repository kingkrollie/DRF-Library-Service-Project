from django.db import transaction
from django.db.models import F
from django.utils import timezone

from rest_framework import mixins, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet

from library.models import Borrowing, Book
from library.permissions import IsOwnerOrStaff, IsAdminOrReadOnly
from library.serializers import (
    BorrowingReadSerializer,
    BorrowingCreateSerializer,
    BookSerializer,
)
from notifications.tasks import notify_new_borrowing
from payment.models import Payment
from payment.services import create_payment_session


class BookViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Book.objects.all().order_by("id")
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly,)

class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    filter_backends = (OrderingFilter,)
    ordering_fields = (
        "borrow_date",
        "expected_return_date",
        "actual_return_date",
    )
    ordering = ("-borrow_date",)

    def get_queryset(self):
        qs = Borrowing.objects.select_related("book", "user")

        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        else:
            user_id = self.request.query_params.get("user_id")
            if user_id and user_id.isdigit():
                qs = qs.filter(user_id=int(user_id))

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            is_active = is_active.strip().lower()
            if is_active in ("true", "1", "yes"):
                qs = qs.filter(actual_return_date__isnull=True)
            elif is_active in ("false", "0", "no"):
                qs = qs.filter(actual_return_date__isnull=False)

        book_id = self.request.query_params.get("book")
        if book_id and book_id.isdigit():
            qs = qs.filter(book_id=book_id)

        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingReadSerializer

    def get_permissions(self):
        if self.action in ("retrieve", "return_book"):
            return (IsAuthenticated(), IsOwnerOrStaff())
        return super().get_permissions()

    @transaction.atomic
    def perform_create(self, serializer):
        book = serializer.validated_data["book"]
        book = Book.objects.select_for_update().get(pk=book.pk)

        if book.inventory <= 0:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"book": "This book is out of stock."})

        borrowing = serializer.save(user=self.request.user)

        Book.objects.filter(pk=book.pk).update(inventory=F("inventory") - 1)

        notify_new_borrowing.delay(borrowing.id)

        return borrowing


class BorrowingDetailView(generics.RetrieveAPIView):
    serializer_class = BorrowingReadSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrStaff)

    def get_queryset(self):
        return Borrowing.objects.select_related("book", "user")

    @action(
        methods=["post"],
        detail=True,
        url_path="return"
    )
    @transaction.atomic
    def return_book(self, request, pk=None):
        borrowing = (
            Borrowing.objects
            .select_related("book", "user")
            .select_for_update()
            .get(pk=pk)
        )

        self.check_object_permissions(request, borrowing)

        if borrowing.actual_return_date is not None:
            return Response(
                {"detail": "This borrowing is already returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        borrowing.actual_return_date = timezone.localdate()
        borrowing.save(update_fields=["actual_return_date"])

        Book.objects.filter(pk=borrowing.book_id).update(
            inventory=F("inventory") + 1)
        if borrowing.actual_return_date >= borrowing.expected_return_date:
            session = create_payment_session(borrowing, is_fee=True)

            Payment.objects.create(
                borrowing=borrowing,
                session_id=session.id,
                session_url=session.url,
                money=session.total_price,
                status=Payment.Status.PENDING,
                type=Payment.Type.FINE,
            )

        serializer = BorrowingReadSerializer(
            borrowing,
            context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
