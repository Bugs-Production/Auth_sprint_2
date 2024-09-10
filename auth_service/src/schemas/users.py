from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field, model_validator

from .mixins import IdMixin


class UserSchema(IdMixin):
    login: str
    first_name: str | None
    last_name: str | None
    email: EmailStr | None
    birthdate: date | None = None

    class Config:
        from_attributes = True


class UpdateUserSchema(BaseModel):
    login: str | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    birthdate: date | None = None

    @model_validator(mode="after")
    def check_at_least_one_field_exists(self):
        if not self.model_fields_set:
            raise ValueError("At least one field required")
        return self


class UserLoginHistorySchema(BaseModel):
    event_date: datetime
    success: bool


class CreateUserSchema(BaseModel):
    login: str = Field(min_length=1)
    password: str = Field(min_length=1)
    first_name: str | None = None
    last_name: str | None = None

    @model_validator(mode="after")
    def check_at_least_one_field_exists(self):
        if not self.model_fields_set:
            raise ValueError("At least one field required")
        return self
