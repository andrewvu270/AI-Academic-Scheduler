from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

# Minimal user schema - no authentication needed
class UserBase(BaseModel):
    id: uuid.UUID

class User(UserBase):
    pass

class UserResponse(UserBase):
    pass