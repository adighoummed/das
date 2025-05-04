from pydantic import BaseModel, validator, field_validator
import re

def validate_israeli_id(id_str: str) -> bool:
    # remove non-digits
    digits = ''.join(filter(str.isdigit, id_str))
    if len(digits) > 9 or len(digits) < 5:
        return False
    digits = digits.zfill(9)
    total = 0
    for i, ch in enumerate(digits):
        digit = int(ch)
        if i % 2 == 0:
            step = digit
        else:
            step = digit * 2
            if step > 9:
                step = step - 9
        total += step
    return total % 10 == 0

class UserBase(BaseModel):
    name: str
    address: str
    phone: str
    national_id: str

    @field_validator('name')
    def name_valid(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Name is required")
        if not re.match(r'^[A-Za-z\s\-]+$', v):
            raise ValueError("Name must contain only letters, spaces, or hyphens")
        return v.strip()

    @field_validator('address')
    def address_valid(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Address is required")
        if len(v.strip()) < 5:
            raise ValueError("Address is too short")
        return v.strip()

    @field_validator('phone')
    def phone_valid(cls, v):
        # accept optional + and 7-15 digits
        if not re.match(r'^\+?\d{7,15}$', v):
            raise ValueError("Invalid phone number format")
        return v

    @field_validator('national_id')
    def national_id_valid(cls, v):
        if not validate_israeli_id(v):
            raise ValueError("Invalid Israeli ID")
        return v

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
