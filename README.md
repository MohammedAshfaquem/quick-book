# QuickBook — Event Booking Platform & Management Backend

QuickBook is a high-performance backend system built with **Python 3.11+**, **Django 5.x**, and **Django REST Framework (DRF)**. It provides a RESTful API for customer event browsing & ticket booking alongside a responsive **Custom Staff Dashboard** for platform administration.

---

## 🚀 Key Features & Highlights

1. **Authentication & User Management**:
   - Custom `User` model using `email` as primary credential.
   - JWT authentication (`access` 60 min, `refresh` 7 days with rotation & blacklisting).
   - Automated unique 8-character uppercase referral code generation (`referral_code`).

2. **Vendor Management**:
   - Explicit URL paths (`/list/`, `/create/`, `<pk>/detail/`, `<pk>/update/`, `<pk>/status/`).
   - Query param filters (`?name=`, `?status=`).

3. **Event Management & Capacity Control**:
   - Real-time seat tracking (`available_seats` & `total_seats`).
   - Explicit date fields (`start_date`, `end_date`, `booking_start_date`, `booking_end_date`).
   - Strict date range validation across both REST API and Staff Dashboard.

4. **Booking System & Concurrency Protection**:
   - **Atomic Concurrency Locking**: Uses `@transaction.atomic` and `select_for_update()` row-level DB locks to prevent ticket overbooking under heavy parallel traffic.
   - Automatic seat decrement on booking creation and seat restoration on cancellation.
   - Auto-generated unique `booking_code` (e.g. `BK-9A8B7C6D`).

5. **Binary Referral Network (BFS Placement)**:
   - Level-order Breadth-First Search (BFS) algorithm to place new referred users into a complete binary tree structure.
   - APIs for full tree visualization (`/tree/`), root node discovery (`/root/`), and left/right team stats (`/stats/`).

6. **Custom Staff Dashboard (`/dashboard/`)**:
   - Session-based staff authentication with modern dark-theme UI.
   - Live metrics summary cards (Total Users, Vendors, Events, Bookings).
   - Full CRUD management for Vendors & Events + Booking cancellation & seat recovery.

7. **Environment Feature Toggles**:
   - Toggle entire modules on/off dynamically via `.env` flags (`EVENT_MODULE`, `BOOKING_MODULE`, `VENDOR_MODULE`, `REFERRAL_MODULE`).
   - Handled via automated middleware returning `403 Forbidden` (`quickbook_feature_disabled`).

8. **Interactive OpenAPI / Swagger Docs**:
   - Live interactive documentation powered by `drf-spectacular` at `/docs/`.

---

## 📂 Project Structure

```
DjangoTask/
├── quickbook/                  # Root Django project settings & URLs
│   ├── settings/
│   │   ├── base.py             # Shared settings & feature flags
│   │   └── local.py            # Local development settings
│   ├── urls.py                 # Root routing table & swagger
│   └── wsgi.py
├── apps/
│   ├── core/                   # Shared mixins, errors, middleware, pagination
│   ├── authentication/         # Custom User, JWT tokens, login/register
│   ├── vendors/                # Vendor CRUD & selectors
│   ├── events/                 # Event scheduling, seat control, date validations
│   ├── bookings/               # Atomic ticket reservations & seat locking
│   ├── referrals/              # Binary Referral Network & BFS placement
│   └── dashboard/              # Custom Staff Dashboard HTML views & templates
├── templates/
│   └── dashboard/              # Staff HTML templates (Dark Theme)
├── static/
│   └── dashboard/              # Vanilla CSS stylesheets & assets
├── manage.py
├── requirements.txt
├── .env.example
└── db.sqlite3
```

---

## 🛠️ Setup & Local Installation

### 1. Clone & Setup Virtual Environment
```bash
git clone <repo-url>
cd DjangoTask

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```

Default `.env` contents:
```env
SECRET_KEY=django-insecure-quickbook-local-dev-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Module Feature Toggles
EVENT_MODULE=True
BOOKING_MODULE=True
VENDOR_MODULE=True
REFERRAL_MODULE=True
```

### 3. Run Database Migrations
```bash
python manage.py migrate
```

### 4. Start Development Server
```bash
python manage.py runserver
```

---

## 🌐 Key URLs & Access Points

| Component | URL | Credentials / Notes |
| :--- | :--- | :--- |
| **Root Redirect** | `http://127.0.0.1:8000/` | Redirects to `/dashboard/` |
| **Staff Dashboard** | `http://127.0.0.1:8000/dashboard/login/` | `ashfaque` / `Password123!` |
| **Interactive Swagger API Docs** | `http://127.0.0.1:8000/docs/` | Test all REST APIs |
| **Django Admin** | `http://127.0.0.1:8000/admin/` | Direct DB view |

---

## 📌 REST API Endpoint Cheat Sheet (`/api/v1/`)

### Authentication (`/api/v1/auth/`)
- `POST /api/v1/auth/register/` — Register new user (optional `referral_code`)
- `POST /api/v1/auth/login/` — Login and receive JWT access & refresh tokens
- `POST /api/v1/auth/logout/` — Blacklist refresh token
- `GET  /api/v1/auth/current-user/` — Current user profile

### Vendors (`/api/v1/vendors/`)
- `POST  /api/v1/vendors/create/`
- `PATCH /api/v1/vendors/<id>/update/`
- `GET   /api/v1/vendors/<id>/detail/`
- `PATCH /api/v1/vendors/<id>/status/`
- `GET   /api/v1/vendors/list/` *(supports `?name=`, `?status=`)*

### Events (`/api/v1/events/`)
- `POST  /api/v1/events/create/`
- `PATCH /api/v1/events/<id>/update/`
- `GET   /api/v1/events/<id>/detail/`
- `PATCH /api/v1/events/<id>/status/`
- `GET   /api/v1/events/list/` *(supports `?name=`, `?status=`, `?vendor=`)*

### Bookings (`/api/v1/bookings/`)
- `POST  /api/v1/bookings/create/` — Reserve tickets (Atomic seat locking)
- `PATCH /api/v1/bookings/<id>/update/`
- `GET   /api/v1/bookings/<id>/detail/`
- `PATCH /api/v1/bookings/<id>/status/` — Cancel booking & restore seats
- `GET   /api/v1/bookings/list/` — Customer/Staff booking list

### Binary Referral Network (`/api/v1/referrals/`)
- `GET /api/v1/referrals/<user_id>/tree/` — Full nested binary tree JSON
- `GET /api/v1/referrals/<user_id>/root/` — Root node lookup
- `GET /api/v1/referrals/<user_id>/stats/` — Left vs right subtree counts
