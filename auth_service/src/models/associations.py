from sqlalchemy import Column, DateTime, ForeignKey, Table, func
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base

user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", UUID(), ForeignKey("users.id"), primary_key=True),
    Column("role_id", UUID(), ForeignKey("roles.id"), primary_key=True),
    Column("created_at", DateTime, server_default=func.now()),
)
