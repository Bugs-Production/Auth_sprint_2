import uuid

from sqlalchemy import Column, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.postgres import Base
from models import OAuthProvidersEnum


class OAuthAccount(Base):
    __tablename__ = "oauth_account"
    __table_args__ = (
        # позволит хранить один и тот же oauth_user_id для разных провайдеров
        UniqueConstraint(
            "oauth_user_id", "provider_type", name="oauth_user_id_provider_type_unique"
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, onupdate="CASCADE"
    )
    user = relationship("User", back_populates="oauth_accounts", lazy=True)
    oauth_user_id = Column(String(length=255))
    provider_type = Column(Enum(OAuthProvidersEnum), nullable=False)
