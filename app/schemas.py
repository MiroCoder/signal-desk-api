from pydantic import BaseModel, Field

class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    id: int
    email: str


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class ProjectResponse(BaseModel):
    id: int
    name: str
    owner_id: int


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)


class TicketCreate(BaseModel):
    title: str = Field(min_length=3)
    description: str
    priority: int = Field(ge=1, le=5)
    project_id: int


class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: int
    project_id: int


class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: int | None = Field(default=None, ge=1, le=5)


class UserLogin(BaseModel):
    email: str
    password: str
