# 🚀 Enterprise Business Management System (EBMS)

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Async-blue)](https://www.postgresql.org/)
[![JWT](https://img.shields.io/badge/JWT-Auth-orange)](https://jwt.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**Enterprise Business Management System** adalah backend system production-ready dengan 10 modul bisnis terintegrasi, dibangun menggunakan **FastAPI** dengan arsitektur modular monolith.

---

## ✨ Features

| Module | Description |
|--------|-------------|
| 🔐 **Auth & Users** | Register, login, JWT, refresh token, role-based access (Admin/Manager/Employee) |
| 🎫 **Ticketing** | Create, update, assign, comments, activity log, status tracking |
| 📄 **Documents** | Upload, download, versioning, permission control |
| 📦 **Inventory** | Products, categories, stock tracking, low stock alerts |
| 🧾 **Invoice** | Create invoices, payments, auto-calculation, status tracking |
| 👥 **HR** | Employees, leave requests, approval workflow |
| 🔔 **Notifications** | User notifications, read/unread tracking |
| 📊 **Reports** | Analytics, summaries, CSV/Excel export |
| 📜 **Audit** | Comprehensive action logging |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Modern web framework |
| **PostgreSQL + Asyncpg** | Async database with connection pooling |
| **SQLAlchemy 2.0** | Async ORM |
| **Alembic** | Database migrations |
| **Pydantic V2** | Data validation |
| **python-jose** | JWT authentication |
| **bcrypt** | Password hashing |
| **Pytest** | Testing framework |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/ebms-fastapi.git
cd ebms-fastapi

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Create database
psql -U postgres
CREATE DATABASE ebms_db;
CREATE USER ebms_user WITH PASSWORD 'strongpassword';
GRANT ALL PRIVILEGES ON DATABASE ebms_db TO ebms_user;
\q

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
Test Credentials
json
{
    "email": "admin@test.com",
    "password": "admin123"
}
📸 Screenshots
Endpoint	Screenshot
Login	https://screenshots/01-login.png
Create Invoice	https://screenshots/02-invoice.png
Create Ticket	https://screenshots/03-ticket.png
Create Product	https://screenshots/04-product.png
Leave Request	https://screenshots/05-leave.png
List Tickets	https://screenshots/06-tickets-list.png
Current User	https://screenshots/07-current-user.png
Swagger UI	https://screenshots/08-swagger-ui.png
Database	https://screenshots/09-database.png
📚 API Documentation
Setelah server running, akses:

Swagger UI: http://localhost:8000/api/docs

ReDoc: http://localhost:8000/api/redoc

🧪 Testing
bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/
🗂️ Project Structure
text
ebms_fastapi/
├── app/
│   ├── core/           # Core configuration, security, database
│   ├── api/v1/         # API endpoints (10 modules)
│   ├── modules/        # Business modules
│   │   ├── auth/       # Authentication & users
│   │   ├── tickets/    # Ticketing system
│   │   ├── documents/  # Document management
│   │   ├── inventory/  # Inventory management
│   │   ├── invoices/   # Invoice system
│   │   ├── hr/         # HR management
│   │   ├── notifications/
│   │   ├── reports/    # Reporting & analytics
│   │   └── audit/      # Audit logging
│   ├── utils/          # Utilities
│   └── tests/          # Unit and integration tests
├── alembic/            # Database migrations
└── requirements.txt
🔒 Security Features
✅ Password hashing with bcrypt

✅ JWT tokens with refresh mechanism

✅ Role-based access control (Admin, Manager, Employee)

✅ SQL injection prevention via ORM

✅ CORS and trusted host middleware

✅ Input validation with Pydantic

✅ Comprehensive audit logging

📊 Database Schema
Table	Description
user	User accounts and roles
ticket	Support tickets
document	File management
product	Inventory products
invoice	Customer invoices
employee	HR records
leave_request	Leave applications
notification	User notifications
audit_log	Activity tracking
📈 Performance Optimizations
✅ Async database operations

✅ Connection pooling

✅ Pagination for large datasets

✅ Gzip compression for responses

✅ Optimized queries with indexes

📄 License
MIT License - feel free to use for your own projects!

🌟 Show Your Support
If this project helped you, please give it a ⭐️!
