from django.urls import path
from .views import verify_paystack_payment

urlpatterns = [
    path('api/paystack/verify/', verify_paystack_payment, name='verify-paystack-payment'),
]
