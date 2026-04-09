# Glamour — Cosmetics E-Commerce System

A full-featured cosmetics e-commerce web application built with Django and Tailwind CSS, connected to a Microsoft SQL Server database.

## Features

- User registration and login with custom user model
- Product catalog with search and category filtering
- Featured products on the home page
- Database-backed shopping cart with quantity management
- Product reviews and star ratings
- eSewa payment gateway integration (sandbox)
- Django admin panel for managing products, categories, reviews, and payments

## Tech Stack

- Python 3.13
- Django 6.0
- Microsoft SQL Server (mssql-django)
- Tailwind CSS (via django-tailwind standalone)
- eSewa ePay v2 API

## Project Structure

```
ecommerce/          # Project settings and URLs
accounts/           # User authentication and registration
products/           # Product catalog and reviews
cart/               # Shopping cart
payments/           # eSewa payment integration
theme/              # Tailwind CSS theme app
```

## Setup

1. Clone the repository and create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create the database `ecommerce_system` in Microsoft SQL Server, then update `HOST` and credentials in `ecommerce/settings.py`.

4. Run migrations:
```bash
python manage.py migrate
```

5. Load initial product data:
```bash
python manage.py loaddata products/fixtures/initial_data.json
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## eSewa Sandbox Credentials

- Product Code: `EPAYTEST`
- Test eSewa Account: `9806800001`
- Password: `Nepal@123`

## Admin

Access the admin panel at `http://127.0.0.1:8000/admin/` to manage products, categories, featured items, reviews, and payments.
