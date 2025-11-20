from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Minimal user schema - no authentication needed
class UserBase(BaseModel):
    id: str

class User(UserBase):
    pass

class UserResponse(UserBase):
    pass