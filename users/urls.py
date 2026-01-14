from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import CreateUserView, ManageUserView, LoginUserView

app_name = "users"
urlpatterns = [
    path("", CreateUserView.as_view(), name="create"),
    path("token/", LoginUserView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
