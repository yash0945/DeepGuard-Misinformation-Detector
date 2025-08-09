from pydantic import BaseModel
from typing import Optional, List

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

# Schemas for Contacts
class ContactBase(BaseModel):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    custom_fields: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class Contact(ContactBase):
    id: int

    class Config:
        from_attributes = True

# Schemas for Groups
class GroupBase(BaseModel):
    name: str

class GroupCreate(GroupBase):
    pass

class Group(GroupBase):
    id: int
    contacts: List[Contact] = []

    class Config:
        from_attributes = True

# Schemas for Templates
class TemplateBase(BaseModel):
    name: str
    subject: Optional[str] = None
    body: Optional[str] = None

class TemplateCreate(TemplateBase):
    pass

class Template(TemplateBase):
    id: int

    class Config:
        from_attributes = True
