import hmac
import hashlib
import base64
import json
import logging
import requests
from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

from cart.models import Cart
from .models import Payment, OrderItem

logger = logging.getLogger(__name__)


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

    # Create the payment record
    payment = Payment.objects.create(
        user=request.user,
        transaction_uuid=transaction_uuid,
        amount=subtotal,
        tax_amount=tax,
        total_amount=total,
        status='PENDING',
    )

    # Snapshot cart items into OrderItems immediately so they're preserved
    # regardless of whether payment succeeds or fails
    cart_items = list(cart.items.select_related('product').all())
    for ci in cart_items:
        OrderItem.objects.create(
            payment=payment,
            product_name=ci.product.name,
            product_price=ci.product.price,
            quantity=ci.quantity,
            subtotal=ci.get_subtotal(),
        )

    # Clear the cart now — items are safe in OrderItem
    cart.items.all().delete()

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
    transaction_code = response_data.get('transaction_code', '')

    payment = Payment.objects.filter(
        transaction_uuid=transaction_uuid,
        user=request.user
    ).first()

    if not payment:
        messages.error(request, 'Payment record not found.')
        return redirect('cart_detail')

    # Always verify directly with eSewa — never trust the client-supplied status
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

            # OrderItems were already created at checkout — just send confirmation
            order_items = list(payment.items.all())
            from mailer.email_utils import send_order_confirmation
            send_order_confirmation(request.user, payment, order_items)

            return render(request, 'payments/success.html', {'payment': payment})

        # eSewa confirmed the payment is not complete
        payment.status = 'FAILED'
        payment.save()
        messages.error(request, 'Payment was not completed. Please try again.')
        return redirect('cart_detail')

    except Exception as e:
        logger.error(f"eSewa verification error for {transaction_uuid}: {e}")
        messages.error(request, 'Payment verification failed. Please contact support.')
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

    messages.error(request, 'Payment was not completed. You can retry it from your order history.')
    return redirect('order_history')


@login_required
def order_history(request):
    orders = (
        Payment.objects
        .filter(user=request.user)
        .prefetch_related('items')
        .order_by('-created_at')
    )
    return render(request, 'payments/order_history.html', {'orders': orders})


@login_required
def cancel_order(request, order_id):
    if request.method != 'POST':
        return redirect('order_history')

    payment = Payment.objects.filter(
        id=order_id,
        user=request.user,
        status__in=['PENDING', 'FAILED']
    ).first()

    if not payment:
        messages.error(request, 'This order cannot be cancelled.')
        return redirect('order_history')

    payment.status = 'CANCELLED'
    payment.save()
    messages.success(request, f'Order #{payment.transaction_uuid[:12].upper()} has been cancelled.')
    return redirect('order_history')


@login_required
def retry_payment(request, order_id):
    payment = Payment.objects.filter(
        id=order_id,
        user=request.user,
        status__in=['PENDING', 'FAILED']
    ).first()

    if not payment:
        messages.error(request, 'This order cannot be retried.')
        return redirect('order_history')

    # Generate a fresh transaction UUID and signature for the retry
    new_uuid = generate_transaction_uuid()
    payment.transaction_uuid = new_uuid
    payment.status = 'PENDING'
    payment.ref_id = ''
    payment.save()

    signature = generate_signature(payment.total_amount, new_uuid, settings.ESEWA_PRODUCT_CODE)

    context = {
        'amount': payment.amount,
        'tax_amount': payment.tax_amount,
        'total_amount': payment.total_amount,
        'transaction_uuid': new_uuid,
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
