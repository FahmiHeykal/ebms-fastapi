# 🚀 Enterprise Business Management System (EBMS)

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Async-blue)
![JWT](https://img.shields.io/badge/JWT-Auth-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📌 Tentang Project

**Enterprise Business Management System (EBMS)** adalah backend system dengan 10 modul bisnis terintegrasi, dibangun menggunakan **FastAPI** dengan arsitektur modular monolith.

---

## 🎯 Fitur Utama

| Modul | Deskripsi |
|-------|-----------|
| 🔐 Auth & Users | Register, login, JWT, refresh token, RBAC (Admin/Manager/Employee) |
| 🎫 Ticketing | Create, update, assign, comments, status tracking, activity log |
| 📄 Documents | Upload, download, versioning, permission control |
| 📦 Inventory | Products, stock tracking, low stock alerts |
| 🧾 Invoice | Create invoices, payments, auto-calculation |
| 👥 HR | Employees, leave requests, approval workflow |
| 🔔 Notifications | User notifications, read/unread tracking |
| 📊 Reports | Analytics, summaries, CSV/Excel export |
| 📜 Audit | Track semua user actions, IP logging |

---

## 🛠️ Tech Stack

- **FastAPI** - Web framework
- **PostgreSQL + Asyncpg** - Async database
- **SQLAlchemy 2.0** - Async ORM
- **Alembic** - Database migrations
- **Pydantic V2** - Data validation
- **JWT + bcrypt** - Authentication & security
- **Pytest** - Testing

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/ebms-fastapi.git
cd ebms-fastapi
```

```bash
# Virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

```bash
# Install dependencies
pip install -r requirements.txt
```

```bash
# Setup database (PostgreSQL)
psql -U postgres
CREATE DATABASE ebms_db;
CREATE USER ebms_user WITH PASSWORD 'strongpassword';
GRANT ALL PRIVILEGES ON DATABASE ebms_db TO ebms_user;
\q
```

```bash
# Copy config
cp .env.example .env
# Edit .env with your database URL
```

```bash
# Run migrations
alembic upgrade head
```

```bash
# Start server
uvicorn app.main:app --reload
Server: http://localhost:8000
```

Test Credentials
{
    "email": "admin@test.com",
    "password": "admin123"
}

📚 API Documentation
Swagger UI: http://localhost:8000/api/docs

ReDoc: http://localhost:8000/api/redoc

📁 Struktur Project
ebms_fastapi/
├── app/
│   ├── core/          # Config, database, security
│   ├── api/v1/        # API endpoints
│   ├── modules/       # 10 business modules
│   └── tests/         # Unit tests
├── alembic/           # Migrations
└── requirements.txt
