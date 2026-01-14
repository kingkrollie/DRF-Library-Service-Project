from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from library.models import Borrowing, Book
from library.permissions import IsOwnerOrStaff
from library.serializers import (
    BorrowingReadSerializer,
    BorrowingCreateSerializer,
)


class BorrowingListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

    filter_backends = (OrderingFilter,)
    ordering_fields = ("borrow_date",
                       "expected_return_date",
                       "actual_return_date")
    ordering = ("-borrow_date",)

    def get_queryset(self):
        qs = Borrowing.objects.select_related("book", "user")
        
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)

        is_active = self.request.GET.get("is_active")
        if is_active is not None:
            is_active = is_active.strip().lower()
            if is_active in ("true", "1", "yes"):
                qs = qs.filter(actual_return_date__isnull=True)
            elif is_active in ("false", "0", "no"):
                qs = qs.filter(actual_return_date__isnull=False)

        book_id = self.request.GET.get("book")
        if book_id:
            qs = qs.filter(book_id=book_id)

        return qs

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BorrowingCreateSerializer
        return BorrowingReadSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        book = serializer.validated_data["book"]
        book = Book.objects.select_for_update().get(pk=book.pk)

        if book.inventory <= 0:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"book": "This book is out of stock."})

        borrowing = serializer.save(user=self.request.user)

        Book.objects.filter(pk=book.pk).update(inventory=F("inventory") - 1)
        return borrowing


class BorrowingDetailView(generics.RetrieveAPIView):
    serializer_class = BorrowingReadSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrStaff)

    def get_queryset(self):
        return Borrowing.objects.select_related("book", "user")

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj
    
    
class BorrowingReturnView(APIView):
    permission_classes = (IsAuthenticated, IsOwnerOrStaff)

    @transaction.atomic
    def post(self, request, pk):
        borrowing = (
            Borrowing.objects.select_related("book", "user")
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

        return Response(BorrowingReadSerializer(borrowing).data, 
                        status=status.HTTP_200_OK)
