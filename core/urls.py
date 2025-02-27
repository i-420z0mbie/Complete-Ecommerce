from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import CreateUserView
from django.urls import path, include


urlpatterns = [
    path('api/user/create/', CreateUserView.as_view(), name='create-user'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='refresh-token'),
    path('api-auth/', include('rest_framework.urls')),
]