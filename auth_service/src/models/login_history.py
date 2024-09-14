import uuid

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Text,
                        UniqueConstraint, func, text)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.postgres import Base


def create_monthly_partitions(target, connection, **kw):
    """Партицирование на 12 месяцев."""
    for month in range(1, 13):
        connection.execute(
            text(
                f"""
            CREATE TABLE IF NOT EXISTS login_history_{month:02d} 
            PARTITION OF login_history 
            FOR VALUES FROM ('2024-{month:02d}-01') TO ('2024-{month+1 if month < 12 else 1:02d}-01');
            """
            )
        )


class LoginHistory(Base):
    __tablename__ = "login_history"
    __table_args__ = (
        UniqueConstraint("id", "event_date"),
        {
            "postgresql_partition_by": "RANGE (event_date)",
            "listeners": [("after_create", create_monthly_partitions)],
        },
    )

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
    user_agent = Column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"<LoginHistory {self.user_id} at {self.event_date}>"
