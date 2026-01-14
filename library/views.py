from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from library.models import Book
from library.serializers import BookSerializer
from library.permissions import IsAdminOrIfAuthenticatedReadOnly


class BookViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)



