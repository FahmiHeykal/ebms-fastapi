from app.api.v1.endpoints import auth
from app.api.v1.endpoints import users
from app.api.v1.endpoints import tickets
from app.api.v1.endpoints import documents
from app.api.v1.endpoints import inventory
from app.api.v1.endpoints import invoices
from app.api.v1.endpoints import hr
from app.api.v1.endpoints import notifications
from app.api.v1.endpoints import reports
from app.api.v1.endpoints import audit

__all__ = [
    "auth", "users", "tickets", "documents", "inventory",
    "invoices", "hr", "notifications", "reports", "audit"
]