from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class LoginUserView(TokenObtainPairView):
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]
    serializer_class = AuthTokenSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user