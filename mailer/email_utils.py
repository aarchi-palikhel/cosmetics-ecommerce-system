from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def send_order_confirmation(user, payment, cart_items):
    salutation = 'Mr.' if user.first_name else ''

    # Build items table rows
    items_html = ''
    items_text = ''
    for item in cart_items:
        subtotal = item.product.price * item.quantity
        items_html += f"""
        <tr>
            <td style="padding:10px;border-bottom:1px solid #F3F4F6;color:#374151;">{item.product.name}</td>
            <td style="padding:10px;border-bottom:1px solid #F3F4F6;color:#374151;text-align:center;">{item.quantity}</td>
            <td style="padding:10px;border-bottom:1px solid #F3F4F6;color:#374151;text-align:right;">Rs. {item.product.price}</td>
            <td style="padding:10px;border-bottom:1px solid #F3F4F6;color:#7C3AED;font-weight:bold;text-align:right;">Rs. {subtotal}</td>
        </tr>
        """
        items_text += f"  - {item.product.name} x{item.quantity} — Rs. {subtotal}\n"

    display_name = user.get_full_name() or user.username

    subject = f"Order Confirmed — Glamour #{payment.transaction_uuid[:12].upper()}"

    text_body = f"""Dear {display_name},

Thank you for your order at Glamour!

Order ID: {payment.transaction_uuid[:12].upper()}
eSewa Ref: {payment.ref_id or 'N/A'}

Items Ordered:
{items_text}
Subtotal:   Rs. {payment.amount}
VAT (13%):  Rs. {payment.tax_amount}
Total Paid: Rs. {payment.total_amount}

Your order has been confirmed and will be processed shortly.

With warm regards,
The Glamour Team
"""

    html_body = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;border:1px solid #E5E7EB;border-radius:12px;overflow:hidden;">

        <!-- Header -->
        <div style="background:linear-gradient(135deg,#7C3AED,#EC4899);padding:28px 30px;text-align:center;">
            <h1 style="color:white;margin:0;font-size:26px;letter-spacing:1px;">Glamour</h1>
            <p style="color:#F3E8FF;margin:6px 0 0;font-size:13px;">Your Beauty Destination in Nepal</p>
        </div>

        <!-- Confirmation Banner -->
        <div style="background:#F0FDF4;padding:16px 30px;border-bottom:1px solid #D1FAE5;text-align:center;">
            <p style="color:#065F46;font-weight:bold;font-size:16px;margin:0;">
                Order Confirmed!
            </p>
            <p style="color:#6B7280;font-size:13px;margin:4px 0 0;">
                Order ID: <strong>#{payment.transaction_uuid[:12].upper()}</strong>
                &nbsp;|&nbsp; eSewa Ref: <strong>{payment.ref_id or 'N/A'}</strong>
            </p>
        </div>

        <!-- Body -->
        <div style="padding:30px;background:#fff;">
            <p style="font-size:16px;color:#1F2937;margin-bottom:20px;">
                Dear <strong>{display_name}</strong>,<br>
                <span style="color:#6B7280;font-size:14px;">Thank you for shopping at Glamour. Here's your order summary.</span>
            </p>

            <!-- Items Table -->
            <table style="width:100%;border-collapse:collapse;font-size:14px;">
                <thead>
                    <tr style="background:#F9FAFB;">
                        <th style="padding:10px;text-align:left;color:#6B7280;font-weight:600;border-bottom:2px solid #E5E7EB;">Product</th>
                        <th style="padding:10px;text-align:center;color:#6B7280;font-weight:600;border-bottom:2px solid #E5E7EB;">Qty</th>
                        <th style="padding:10px;text-align:right;color:#6B7280;font-weight:600;border-bottom:2px solid #E5E7EB;">Price</th>
                        <th style="padding:10px;text-align:right;color:#6B7280;font-weight:600;border-bottom:2px solid #E5E7EB;">Subtotal</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>

            <!-- Totals -->
            <div style="margin-top:16px;padding:16px;background:#F9FAFB;border-radius:8px;font-size:14px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                    <span style="color:#6B7280;">Subtotal</span>
                    <span style="color:#374151;">Rs. {payment.amount}</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-bottom:10px;">
                    <span style="color:#6B7280;">VAT (13%)</span>
                    <span style="color:#374151;">Rs. {payment.tax_amount}</span>
                </div>
                <div style="display:flex;justify-content:space-between;border-top:1px solid #E5E7EB;padding-top:10px;">
                    <span style="color:#1F2937;font-weight:bold;">Total Paid</span>
                    <span style="color:#7C3AED;font-weight:bold;font-size:16px;">Rs. {payment.total_amount}</span>
                </div>
            </div>

            <p style="color:#6B7280;font-size:13px;margin-top:20px;">
                Your order has been confirmed and will be processed shortly. Thank you for choosing Glamour!
            </p>

            <div style="text-align:center;margin-top:24px;">
                <a href="http://127.0.0.1:8000/products/"
                    style="background:linear-gradient(135deg,#7C3AED,#EC4899);color:white;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:bold;font-size:14px;">
                    Continue Shopping
                </a>
            </div>
        </div>

        <!-- Footer -->
        <div style="background:#F9FAFB;padding:16px 30px;text-align:center;font-size:12px;color:#9CA3AF;border-top:1px solid #E5E7EB;">
            &copy; 2026 Glamour Cosmetics Nepal. All rights reserved.
        </div>
    </div>
    """

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()
    except Exception as e:
        print(f"Order confirmation email failed: {e}")
