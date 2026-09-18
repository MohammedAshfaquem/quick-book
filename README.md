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
   - Profile management including optional `logo_url` and contact phone validation.

3. **Event Management & Capacity Control**:
   - **Real-time Seat Tracking**: Dynamic seat inventory management (`total_seats`, `available_seats`, `reserved_seats`) with custom per-booking limits (`min_seats_per_booking`, `max_seats_per_booking`).
   - **6 Explicit Date & Time Fields**:
     1. `start_date` — Overall event window start
     2. `end_date` — Overall event window end
     3. `booking_start_date` — Ticket sales open timestamp
     4. `booking_end_date` — Ticket sales cutoff timestamp (optional)
     5. `show_start_date` — Performance/Show start timestamp
     6. `show_end_date` — Performance/Show end timestamp
   - **4 Dynamic Show Statuses**:
     - 🟢 `upcoming` — Show scheduled; booking window not yet open.
     - 🎫 `booking_enabled` — Tickets currently active and available for purchase.
     - 🎭 `running` — Show is currently live in progress.
     - 🏁 `expired` — Show has concluded.
   - **Visual Assets**: Includes optional `banner_url` for event posters/banners.
   - **Strict Validation Rules**: Venue conflict detection (no overlapping active events at the same venue) + date ordering checks across REST API and Staff Dashboard.

4. **Booking System & Concurrency Protection**:
   - **Atomic Concurrency Locking**: Uses `@transaction.atomic` and `select_for_update()` row-level DB locks to prevent ticket overbooking under heavy parallel traffic.
   - **4 Booking Statuses**:
     - ⏳ `pending` — Booking reservation created; awaiting confirmation/payment.
     - ✅ `confirmed` — Tickets confirmed & seats locked.
     - ❌ `cancelled` — Booking cancelled & seats automatically restored to inventory.
     - ⚠️ `failed` — Booking attempt failed.
   - Automatic seat decrement on booking creation and seat restoration on cancellation.
   - Auto-generated unique `booking_code` (e.g. `BK-9A8B7C6D`).

5. **Binary Referral Network (BFS Placement)**:
   - Level-order Breadth-First Search (BFS) algorithm to place new referred users into a complete binary tree structure.
   - APIs for full tree visualization (`/tree/`), root node discovery (`/root/`), and left/right team stats (`/stats/`).

6. **Custom Staff Dashboard (`/dashboard/`)**:
   - Session-based staff authentication with modern dark-theme UI.
   - Live metrics summary cards (Total Users, Vendors, Events, Bookings).
   - Full CRUD management for Vendors & Events + Booking cancellation & seat recovery.

7. **Environment Feature Toggles & System Configurations**:
   - **API Module Toggles**: Dynamically enable/disable entire API domains via `.env` flags (`EVENT_MODULE`, `BOOKING_MODULE`, `VENDOR_MODULE`, `REFERRAL_MODULE`). Enforced by automated middleware returning `403 Forbidden` (`quickbook_feature_disabled`).
   - **Payment Gateway Toggle**: `ENABLE_PAYMENT_GATEWAY` flag toggles automatic payment webhook processing vs manual status updates.
   - **Booking Hold Timeout Config**: `BOOKING_TIME_MINUTES` sets the reservation hold period in minutes before pending bookings expire.
   - **JWT Token Lifetime Configs**: `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` and `JWT_REFRESH_TOKEN_LIFETIME_DAYS` dynamically control JWT token expiration periods.

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

# Payment & Hold Settings
ENABLE_PAYMENT_GATEWAY=False
BOOKING_TIME_MINUTES=15

# JWT Token Lifetimes
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
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
| **Staff Dashboard** | `http://127.0.0.1:8000/dashboard/login/`
| **Interactive Swagger API Docs** | `http://127.0.0.1:8000/docs/` | Test all REST APIs |
| **Django Admin** | `http://127.0.0.1:8000/admin/` | Direct DB view |

---

## 📌 REST API Endpoint Cheat Sheet (`/api/v1/`)

### Authentication (`/api/v1/auth/`)
- `POST /api/v1/auth/register/` — Register new user (optional `referral_code`)
- `POST /api/v1/auth/login/` — Login and receive JWT access & refresh tokens
- `POST /api/v1/auth/logout/` — Blacklist refresh token
- `POST /api/v1/auth/token/refresh/` — Obtain new access token using refresh token
- `GET  /api/v1/auth/current-user/` — Current logged-in user profile
- `PATCH /api/v1/auth/current-user/` — Update logged-in user profile (`first_name`, `last_name`, `username`, `email`)
- `GET  /api/v1/auth/users/` — Staff-only user list *(supports pagination & filtering)*
- `POST /api/v1/auth/change-password/` — Authenticated user password change

### Vendors (`/api/v1/vendors/`)
- `POST  /api/v1/vendors/create/` — Create new vendor profile
- `PATCH /api/v1/vendors/<id>/update/` — Partial update vendor details
- `GET   /api/v1/vendors/<id>/detail/` — View single vendor details
- `PATCH /api/v1/vendors/<id>/status/` — Toggle vendor active/inactive status
- `GET   /api/v1/vendors/list/` — Paginated vendor list *(supports `?name=`, `?status=`)*

### Events (`/api/v1/events/`)
- `POST  /api/v1/events/create/` — Create new event
- `PATCH /api/v1/events/<id>/update/` — Partial update event details & schedules
- `GET   /api/v1/events/<id>/detail/` — View single event details & calculated `show_status`
- `PATCH /api/v1/events/<id>/status/` — Toggle event active/inactive status
- `GET   /api/v1/events/list/` — Paginated event list *(supports `?search=`, `?status=`, `?show_status=`, `?vendor=`)*

### Bookings (`/api/v1/bookings/`)
- `POST  /api/v1/bookings/create/` — Reserve tickets with atomic seat locking
- `PATCH /api/v1/bookings/<id>/update/` — Partial update booking
- `GET   /api/v1/bookings/<id>/detail/` — View single booking details
- `PATCH /api/v1/bookings/<id>/status/` — Cancel booking & restore seat inventory
- `GET   /api/v1/bookings/list/` — User / Staff booking list *(supports `?status=`, `?event=`)*
- `POST  /api/v1/bookings/cleanup/` — Cleanup maintenance task for expired pending reservations

### Binary Referral Network (`/api/v1/referrals/`)
- `GET /api/v1/referrals/<user_id>/tree/` — Full nested binary tree JSON
- `GET /api/v1/referrals/<user_id>/root/` — Root node lookup
- `GET /api/v1/referrals/<user_id>/stats/` — Left vs right subtree counts

---

## 🖥️ Staff Dashboard Route Cheat Sheet (`/dashboard/`)

| Route | Description |
| :--- | :--- |
| `GET /dashboard/login/` | Staff login page |
| `GET /dashboard/logout/` | Staff logout |
| `GET /dashboard/overview/` | Admin overview metrics & recent activity |
| `GET /dashboard/vendors/list/` | Vendor management table |
| `GET /dashboard/vendors/add/` | Add new vendor form |
| `GET /dashboard/vendors/<pk>/detail/` | Vendor profile & analytics |
| `GET /dashboard/vendors/<pk>/edit/` | Edit vendor form |
| `POST /dashboard/vendors/<pk>/status/` | Toggle vendor active status |
| `GET /dashboard/events/list/` | Event management table |
| `GET /dashboard/events/add/` | Schedule new event form |
| `GET /dashboard/events/<pk>/detail/` | Event details & show status |
| `GET /dashboard/events/<pk>/edit/` | Edit event form |
| `POST /dashboard/events/<pk>/status/` | Toggle event active status |
| `GET /dashboard/bookings/list/` | Master bookings table |
| `GET /dashboard/bookings/<pk>/detail/` | View booking & customer details |
| `POST /dashboard/bookings/<pk>/cancel/` | Cancel booking & restore seats |
| `GET /dashboard/users/list/` | System user directory |
| `GET /dashboard/users/add/` | Add new Customer or Staff user form (Superadmin only) |
| `GET /dashboard/users/<pk>/detail/` | User profile & referral overview |
| `GET /dashboard/users/<pk>/edit/` | Edit user profile & account settings form |
| `POST /dashboard/users/<pk>/toggle-staff/` | Grant/Revoke staff permissions |

