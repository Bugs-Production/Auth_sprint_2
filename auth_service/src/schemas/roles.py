from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from schemas.mixins import IdMixin


class RoleSchema(IdMixin):
    title: str


class RoleCreateSchema(BaseModel):
    title: str


class RoleUpdateSchema(BaseModel):
    role_id: UUID = Field(default_factory=uuid4, serialization_alias="id")
