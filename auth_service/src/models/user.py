import uuid

from sqlalchemy import Column, Date, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from db.postgres import Base
from models.associations import user_role
from models.sqlalchemy_utils.email import EmailType


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(EmailType)
    birthdate = Column(Date)
    created_at = Column(DateTime, default=func.now())
    roles = relationship("Role", secondary=user_role, backref="users", cascade="all, delete")
    login_history = relationship("LoginHistory", back_populates="user", cascade="all, delete")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete")

    def __init__(
        self, login: str, password: str, first_name: str, last_name: str
    ) -> None:
        self.login = login
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f"<User {self.login}>"
