import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    title = Column(String(50), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Role {self.title}>"
