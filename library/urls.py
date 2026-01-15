from django.urls import path, include
from rest_framework.routers import DefaultRouter
from library.views import (
    BookViewSet,
    BorrowingListCreateView,
    BorrowingDetailView,
    BorrowingReturnView,
)

app_name = "library"
router = DefaultRouter()
router.register("books", BookViewSet, basename="book")

urlpatterns = [
    path("", include(router.urls)),
    path("borrowings/", BorrowingListCreateView.as_view(),
         name="borrowing-list-create"),
    path("borrowings/<int:pk>/", BorrowingDetailView.as_view(),
         name="borrowing-detail"),
    path("borrowings/<int:pk>/return/", BorrowingReturnView.as_view(), 
         name="borrowing-return"),
]
