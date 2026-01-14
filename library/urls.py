from django.urls import path
from library.views import (
    BorrowingListCreateView,
    BorrowingDetailView,
    BorrowingReturnView,
)

urlpatterns = [
    path("borrowings/", BorrowingListCreateView.as_view(),
         name="borrowing-list-create"),
    path("borrowings/<int:pk>/", BorrowingDetailView.as_view(),
         name="borrowing-detail"),
    path("borrowings/<int:pk>/return/", BorrowingReturnView.as_view(), 
         name="borrowing-return"),
]
