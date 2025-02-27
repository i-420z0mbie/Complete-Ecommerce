from rest_framework.generics import CreateAPIView
from django.contrib.auth.models import User
from .serializers import CreateUserSerializer
from rest_framework.permissions import AllowAny



class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        
        serializer.save()