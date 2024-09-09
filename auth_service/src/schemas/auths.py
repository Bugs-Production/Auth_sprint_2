from pydantic import BaseModel, Field


class AuthOutputSchema(BaseModel):
    access_token: str
    refresh_token: str


class RefreshInputSchema(BaseModel):
    refresh_token: str
    access_token: str


class LoginInputSchema(BaseModel):
    login: str = Field(min_length=1)
    password: str = Field(min_length=1)
