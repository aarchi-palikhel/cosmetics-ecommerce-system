import csv
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def read_csv():
    contacts = []
    try:
        with open(settings.EMAIL_CSV_PATH, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                contacts.append({
                    'name': row['Name'].strip(),
                    'location': row['Location'].strip(),
                    'email': row['EmailID'].strip(),
                    'gender': row['Gender'].strip(),
                    'salutation': 'Mr.' if row['Gender'].strip().lower() == 'male' else 'Ms.',
                })
    except FileNotFoundError:
        pass
    return contacts


@user_passes_test(is_admin, login_url='home')
def compose(request):
    contacts = read_csv()
    preview = contacts[0] if contacts else None

    if request.method == 'POST':
        subject_template = request.POST.get('subject', '')
        body_template = request.POST.get('body', '')

        sent = 0
        failed = 0
        results = []

        for contact in contacts:
            subject = subject_template \
                .replace('{name}', contact['name']) \
                .replace('{location}', contact['location']) \
                .replace('{gender}', contact['gender']) \
                .replace('{salutation}', contact['salutation'])

            body_text = body_template \
                .replace('{name}', contact['name']) \
                .replace('{location}', contact['location']) \
                .replace('{gender}', contact['gender']) \
                .replace('{salutation}', contact['salutation'])

            html_body = f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;border:1px solid #E5E7EB;border-radius:12px;overflow:hidden;">
                <!-- Header -->
                <div style="background:linear-gradient(135deg,#7C3AED,#EC4899);padding:30px;text-align:center;">
                    <h1 style="color:white;margin:0;font-size:28px;letter-spacing:1px;">Glamour</h1>
                    <p style="color:#F3E8FF;margin:6px 0 0;font-size:13px;">Your Beauty Destination in Nepal</p>
                </div>

                <!-- Body -->
                <div style="padding:30px;background:#fff;">
                    <p style="font-size:18px;color:#1F2937;margin-bottom:16px;">
                        Hello, <strong>{contact['salutation']} {contact['name']}!</strong>
                    </p>
                    <div style="color:#4B5563;line-height:1.8;white-space:pre-line;font-size:14px;">{body_text}</div>

                    <!-- CTA Button -->
                    <div style="text-align:center;margin-top:30px;">
                        <a href="http://127.0.0.1:8000"
                            style="background:linear-gradient(135deg,#7C3AED,#EC4899);color:white;padding:12px 32px;border-radius:8px;text-decoration:none;font-weight:bold;font-size:14px;">
                            Visit Glamour Store
                        </a>
                    </div>
                </div>

                <!-- Footer -->
                <div style="background:#F9FAFB;padding:16px 30px;text-align:center;font-size:12px;color:#9CA3AF;border-top:1px solid #E5E7EB;">
                    &copy; 2026 Glamour Cosmetics Nepal. All rights reserved.<br>
                    You are receiving this email because you are a registered member.
                </div>
            </div>
            """

            try:
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=body_text,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[contact['email']],
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send()
                sent += 1
                results.append({'contact': contact, 'status': 'sent'})
            except Exception:
                failed += 1
                results.append({'contact': contact, 'status': 'failed'})

        return render(request, 'mailer/report.html', {
            'results': results,
            'sent': sent,
            'failed': failed,
            'total': len(contacts),
            'subject': subject_template,
        })

    # Build preview with first contact
    default_subject = "Welcome to Glamour — Your Beauty Journey Starts Here, {name}!"
    default_body = """Dear {salutation} {name},

We are thrilled to welcome you to Glamour, Nepal's premier online cosmetics store.

As a valued member from {location}, we have curated the finest skincare, makeup, haircare, and fragrance products just for you.

Here's what you can enjoy as a Glamour member:

  - Exclusive discounts on premium cosmetics
  - Free delivery on orders above Rs. 2,000
  - Early access to new product launches
  - Special offers tailored for you

Visit our store today and discover beauty products crafted for every skin type.

With warm regards,
The Glamour Team
www.glamour.com.np"""

    return render(request, 'mailer/compose.html', {
        'contacts': contacts,
        'total': len(contacts),
        'preview': preview,
        'default_subject': default_subject,
        'default_body': default_body,
    })
