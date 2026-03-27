# 🚀 Enterprise Business Management System (EBMS)

## FastAPI Modular Monolith with 10 Business Modules

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Async-blue)
![JWT](https://img.shields.io/badge/JWT-Auth-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Overview

**Enterprise Business Management System** is a production-ready backend system built with **FastAPI**, featuring a modular monolith architecture with **10 integrated business modules**.

### 🎯 Key Features
- ✅ **JWT Authentication** with refresh tokens
- ✅ **Role-Based Access Control** (Admin, Manager, Employee)
- ✅ **Async Database Operations** with PostgreSQL
- ✅ **Comprehensive Audit Logging**
- ✅ **File Upload** with version control
- ✅ **Auto-generated API Documentation** (Swagger/ReDoc)
- ✅ **Pagination & Filtering** for all list endpoints

---

## 🏗️ Architecture
┌─────────────────────────────────────────────────────────────┐
│ CLIENT (Browser/Postman) │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ FASTAPI SERVER │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ API Routes (RESTful - 10 Modules) │ │
│ │ /auth /users /tickets /documents /inventory │ │
│ │ /invoices /hr /notifications /reports /audit │ │
│ └───────────────────────────────────────────────────────┘ │
│ │ │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ Business Logic (Service Layer) │ │
│ │ AuthService | TicketService | InvoiceService │ │
│ │ InventoryService | HRService | AuditService │ │
│ └───────────────────────────────────────────────────────┘ │
│ │ │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ Database Models (SQLAlchemy ORM) │ │
│ │ User | Ticket | Document | Product | Invoice │ │
│ │ Employee | Notification | AuditLog │ │
│ └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ POSTGRESQL DATABASE │
└─────────────────────────────────────────────────────────────┘

---

## 📦 Modules

| Module | Description |
|--------|-------------|
| 🔐 **Auth & Users** | Register, login, JWT, refresh token, RBAC |
| 🎫 **Ticketing** | Create, update, assign, comments, activity log |
| 📄 **Documents** | Upload, download, versioning, permissions |
| 📦 **Inventory** | Products, stock tracking, low stock alerts |
| 🧾 **Invoice** | Create invoices, payments, auto-calculation |
| 👥 **HR** | Employees, leave requests, approval workflow |
| 🔔 **Notifications** | User notifications, read/unread tracking |
| 📊 **Reports** | Analytics, summaries, CSV export |
| 📜 **Audit** | Comprehensive action logging |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Modern web framework |
| **PostgreSQL + Asyncpg** | Async database |
| **SQLAlchemy 2.0** | Async ORM |
| **Alembic** | Database migrations |
| **Pydantic V2** | Data validation |
| **python-jose** | JWT authentication |
| **bcrypt** | Password hashing |

---

## 🚀 Quick Start

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

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload

```

Test Credentials

{
    "email": "admin@test.com",
    "password": "admin123"
}
📸 Screenshots
Login Response
https://screenshots/01-login.png

Create Invoice
https://screenshots/02-invoice.png

Create Ticket
https://screenshots/03-ticket.png

Create Product
https://screenshots/04-product.png

Leave Request
https://screenshots/05-leave.png

List Tickets
https://screenshots/06-tickets-list.png

Current User
https://screenshots/07-current-user.png

Swagger UI
https://screenshots/08-swagger-ui.png

Database Structure
https://screenshots/09-database.png

📚 API Documentation
Once running:

Swagger UI: http://localhost:8000/api/docs

ReDoc: http://localhost:8000/api/redoc

🗂️ Project Structure
ebms_fastapi/
├── app/
│   ├── core/           # Core configuration
│   ├── api/v1/         # API endpoints
│   ├── modules/        # 10 business modules
│   └── tests/          # Tests
├── alembic/            # Migrations
└── requirements.txt

📄 License
MIT License

🌟 Show Your Support
Give a ⭐️ if this project helped you!

---

## ✅ Selesai!
