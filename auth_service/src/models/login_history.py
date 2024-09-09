import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.postgres import Base


class LoginHistory(Base):
    __tablename__ = "login_history"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    event_date = Column(DateTime, default=func.now(), nullable=False)
    success = Column(Boolean, nullable=False)  # True для успеха, False для неудачи
    user = relationship("User", back_populates="login_history")

    def __repr__(self) -> str:
        return f"<LoginHistory {self.user_id} at {self.event_date}>"
