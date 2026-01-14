from django.shortcuts import render
from rest_framework import generics
from library.models import Borrowing
from library.serializers import BorrowingReadSerializer


class BorrowingListView(generics.ListAPIView):
    queryset = Borrowing.objects.select_related("book", "user").all()
    serializer_class = BorrowingReadSerializer


class BorrowingDetailView(generics.RetrieveAPIView):
    queryset = Borrowing.objects.select_related("book", "user").all()
    serializer_class = BorrowingReadSerializer
