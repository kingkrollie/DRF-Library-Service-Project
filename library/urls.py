from django.urls import include, path
from rest_framework.routers import DefaultRouter

from library.views import BookViewSet, BorrowingViewSet

app_name = "library"

router = DefaultRouter()
router.register("books", BookViewSet, basename="book")
router.register("borrowings", BorrowingViewSet, basename="borrowing")

urlpatterns = [
    path("", include(router.urls)),
]
