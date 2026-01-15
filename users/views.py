from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.serializers import UserSerializer, AuthTokenSerializer


@extend_schema_view(
    post=extend_schema(
        description="Create new account for user",
        responses={201: UserSerializer},
    )
)
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class LoginUserView(TokenObtainPairView):
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]
    serializer_class = AuthTokenSerializer


@extend_schema_view(
    get=extend_schema(
        description="Return authorized user profile data"
    ),
    put=extend_schema(
        description="Update user data (full)",
    ),
    patch=extend_schema(
        description="Update user data (partial)",
    )
)
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user