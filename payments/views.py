import hmac
import hashlib
import base64
import json
import requests
from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

from cart.models import Cart
from .models import Payment


def generate_signature(total_amount, transaction_uuid, product_code):
    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    secret = settings.ESEWA_SECRET_KEY.encode()
    sig = hmac.new(secret, message.encode(), hashlib.sha256)
    return base64.b64encode(sig.digest()).decode()


def generate_transaction_uuid():
    # Format: YYMMDD-HHMMSS — alphanumeric and hyphen only as required by eSewa
    return datetime.now().strftime("%y%m%d-%H%M%S")


@login_required
def initiate_payment(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart_detail')

    subtotal = cart.get_subtotal()
    tax = cart.get_tax()
    total = cart.get_total()
    transaction_uuid = generate_transaction_uuid()

    signature = generate_signature(total, transaction_uuid, settings.ESEWA_PRODUCT_CODE)

    # Save pending payment record
    Payment.objects.create(
        user=request.user,
        transaction_uuid=transaction_uuid,
        amount=subtotal,
        tax_amount=tax,
        total_amount=total,
        status='PENDING',
    )

    context = {
        'amount': subtotal,
        'tax_amount': tax,
        'total_amount': total,
        'transaction_uuid': transaction_uuid,
        'product_code': settings.ESEWA_PRODUCT_CODE,
        'product_service_charge': '0',
        'product_delivery_charge': '0',
        'success_url': request.build_absolute_uri('/payments/success/'),
        'failure_url': request.build_absolute_uri('/payments/failure/'),
        'signed_field_names': 'total_amount,transaction_uuid,product_code',
        'signature': signature,
        'payment_url': settings.ESEWA_PAYMENT_URL,
    }
    return render(request, 'payments/esewa_form.html', context)


@login_required
def payment_success(request):
    # eSewa sends response as Base64 encoded JSON in 'data' param
    encoded_data = request.GET.get('data')
    if not encoded_data:
        messages.error(request, 'Invalid payment response.')
        return redirect('cart_detail')

    try:
        decoded = base64.b64decode(encoded_data).decode('utf-8')
        response_data = json.loads(decoded)
    except Exception:
        messages.error(request, 'Could not decode payment response.')
        return redirect('cart_detail')

    transaction_uuid = response_data.get('transaction_uuid')
    status = response_data.get('status')
    transaction_code = response_data.get('transaction_code', '')

    payment = Payment.objects.filter(
        transaction_uuid=transaction_uuid,
        user=request.user
    ).first()

    if not payment:
        messages.error(request, 'Payment record not found.')
        return redirect('cart_detail')

    if status == 'COMPLETE':
        # Verify with eSewa status API
        try:
            verify = requests.get(settings.ESEWA_STATUS_URL, params={
                'product_code': settings.ESEWA_PRODUCT_CODE,
                'transaction_uuid': transaction_uuid,
                'total_amount': str(payment.total_amount),
            }, timeout=10)
            verify_data = verify.json()

            if verify_data.get('status') == 'COMPLETE':
                payment.status = 'COMPLETE'
                payment.ref_id = verify_data.get('ref_id', transaction_code)
                payment.save()
                # Clear cart
                cart = Cart.objects.filter(user=request.user).first()
                if cart:
                    # Capture items before deleting for email
                    cart_items = list(cart.items.select_related('product').all())
                    cart.items.all().delete()

                # Send order confirmation email
                from mailer.email_utils import send_order_confirmation
                send_order_confirmation(request.user, payment, cart_items)

                return render(request, 'payments/success.html', {'payment': payment})
        except Exception:
            pass

    payment.status = 'FAILED'
    payment.save()
    messages.error(request, 'Payment verification failed.')
    return redirect('cart_detail')


@login_required
def payment_failure(request):
    encoded_data = request.GET.get('data')
    transaction_uuid = None

    if encoded_data:
        try:
            decoded = base64.b64decode(encoded_data).decode('utf-8')
            response_data = json.loads(decoded)
            transaction_uuid = response_data.get('transaction_uuid')
        except Exception:
            pass

    if transaction_uuid:
        Payment.objects.filter(
            transaction_uuid=transaction_uuid,
            user=request.user
        ).update(status='FAILED')

    return render(request, 'payments/failure.html')
