from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None


class UserRead(BaseModel):
    user_id: int
    email: EmailStr
    first_name: str
    last_name: str

    class Config:
        from_attributes = True