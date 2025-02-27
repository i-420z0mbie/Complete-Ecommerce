from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import requests
from django.conf import settings
from main.models import Payment, Order
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_paystack_payment(request):
    reference = request.data.get('reference')
    if not reference:
        return Response({'error': 'Payment reference not provided.'}, status=status.HTTP_400_BAD_REQUEST)

    # Call Paystack's verify endpoint.
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}

    try:
        paystack_response = requests.get(url, headers=headers)
    except requests.RequestException as e:
        logger.exception("Error calling Paystack verify endpoint:")
        return Response({'error': 'Error contacting Paystack.'}, status=status.HTTP_502_BAD_GATEWAY)

    if paystack_response.status_code != 200:
        logger.error("Paystack verification failed with status %s", paystack_response.status_code)
        return Response({'error': 'Verification failed with Paystack.'}, status=paystack_response.status_code)

    response_data = paystack_response.json()

    # Check the status in the response.
    if response_data.get('data', {}).get('status') == 'success':
        try:
            payment = Payment.objects.get(payment_reference=reference)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check for idempotency: if already verified, return a success message.
        if payment.is_verified:
            return Response({'message': 'Payment already verified.'}, status=status.HTTP_200_OK)

        # Update payment status and mark as verified.
        payment.status = Payment.STATUS_SUCCESSFUL
        payment.is_verified = True
        payment.save()


        order = payment.order
        order.status = Order.STATUS_PROCESSING
        order.save()


        return Response({'message': 'Payment verified successfully.'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Payment was not successful.'}, status=status.HTTP_400_BAD_REQUEST)
