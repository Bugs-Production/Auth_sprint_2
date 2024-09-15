from pydantic import BaseModel, Field


class AuthOutputSchema(BaseModel):
    access_token: str
    refresh_token: str
    user_id: str


class RefreshInputSchema(BaseModel):
    refresh_token: str
    access_token: str


class LoginInputSchema(BaseModel):
    login: str = Field(min_length=1)
    password: str = Field(min_length=1)


class OAuthUser(BaseModel):
    oauth_user_id: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    provider_type: str
