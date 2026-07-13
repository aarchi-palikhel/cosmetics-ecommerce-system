# Glamour — Cosmetics E-Commerce System

A full-featured cosmetics e-commerce web application built with **Django** and **Tailwind CSS**, backed by **Microsoft SQL Server**. Designed for a Nepal-based beauty store, it covers everything from user authentication to eSewa payment processing and bulk email campaigns.

---

## Features

### Accounts
- Custom user model with email, phone, address, and date of birth fields
- Login with either **username or email** (custom authentication backend)
- User registration, profile editing, and dashboard with order stats

### Products
- Product catalog with category filtering and live **search suggestions**
- Featured products on the home page
- **Product detail** pages with stock status and low-stock indicators
- **Star ratings and reviews** — one review per user per product
- **Wishlist** — toggle products in/out with AJAX support

### Cart
- Persistent, database-backed cart per user
- Add, update, and remove items with **real-time AJAX updates**
- Automatic **13% VAT** calculation with subtotal/tax/total breakdown
- Stock validation — cannot add more than available inventory

### Payments (eSewa ePay v2)
- Seamless **eSewa sandbox** payment flow with HMAC-SHA256 signature
- **Server-side payment verification** — status is always confirmed directly with eSewa (never client-trusted)
- Order items snapshotted at checkout to preserve history regardless of payment outcome
- **Order history** with status badges (Pending, Complete, Failed, Cancelled)
- Retry failed/pending payments with a fresh transaction UUID
- Cancel pending or failed orders

### Mailer (Admin-only)
- Bulk **personalised email campaigns** to contacts loaded from a CSV
- Template variables: `{name}`, `{salutation}`, `{location}`, `{gender}`
- Branded HTML email template with live contact preview before sending
- Send report showing per-contact success/failure status
- Import contacts via CSV through the Django admin panel
- **Automatic order confirmation email** sent to customer on successful payment

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, Django 4.2+ |
| Database | Microsoft SQL Server (`mssql-django`) |
| Frontend | Tailwind CSS via `django-tailwind` |
| Payments | eSewa ePay v2 API (sandbox) |
| Email | Django SMTP (Gmail) |
| Images | Pillow |
| HTTP | `requests` library |
| Config | `python-dotenv` |

---

## Project Structure

```
ecommerce_system/
├── ecommerce/          # Project settings and root URLs
├── accounts/           # Custom user model, auth, registration, dashboard, profile
├── products/           # Product catalog, categories, reviews, wishlist
├── cart/               # Shopping cart and cart items
├── payments/           # eSewa payment flow, order history, order items
├── mailer/             # Bulk email campaigns and contact management
├── theme/              # Tailwind CSS theme app
├── media/              # Uploaded product images
└── manage.py
```

---

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd Ecommerce_system
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

ESEWA_SECRET_KEY=8gBm/:&EnhH.1/q

EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

> For Gmail, generate an **App Password** (not your login password) at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).

### 4. Configure the database

Create a database named `ecommerce_system` in Microsoft SQL Server, then update the `HOST` in `ecommerce/settings.py` to match your SQL Server instance name:

```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'ecommerce_system',
        'HOST': 'YOUR-SERVER-NAME',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'trusted_connection': 'yes',
        },
    }
}
```

An SQLite fallback is also commented out in `settings.py` if needed for local development.

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. (Optional) Load sample product data

```bash
python manage.py loaddata products/fixtures/initial_data.json
```

### 8. Start the development server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000`

---

## eSewa Sandbox Credentials

Use these to test payments without real money:

| Field | Value |
|---|---|
| Product Code | `EPAYTEST` |
| Test eSewa ID | `9806800001` |
| Password | `Nepal@123` |

---

## Admin Panel

Access at `http://127.0.0.1:8000/admin/`

Manage products, categories, reviews, payments, and mail contacts. The mailer also supports importing contacts from a CSV file directly through the admin interface.

---

## Bulk Email Campaign

Staff/superuser accounts can access the mailer at `http://127.0.0.1:8000/mailer/compose/`.

Supported template variables in subject and body:

| Variable | Replaced with |
|---|---|
| `{name}` | Contact's full name |
| `{salutation}` | `Mr.` or `Ms.` based on gender |
| `{location}` | Contact's location |
| `{gender}` | Contact's gender value |

Contacts are managed through the admin panel and can be bulk-imported via a CSV with columns: `name`, `email`, `location`, `gender`.

---

## URL Overview

| URL | Description |
|---|---|
| `/` | Home page with featured products |
| `/accounts/register/` | User registration |
| `/accounts/login/` | Login (username or email) |
| `/accounts/dashboard/` | User dashboard |
| `/accounts/profile/` | Edit profile |
| `/products/` | Full product catalog |
| `/products/<id>/` | Product detail, reviews, wishlist |
| `/cart/` | Shopping cart |
| `/payments/checkout/` | Initiate eSewa payment |
| `/payments/orders/` | Order history |
| `/mailer/compose/` | Bulk email composer (admin only) |
| `/admin/` | Django admin panel |
