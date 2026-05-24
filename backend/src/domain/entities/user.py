# src/domain/entities/user.py
from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class User:
    id: UUID
    role_id: UUID
    full_name: str
    email: str
    phone: Optional[str]
    is_active: bool = True
    role_name: Optional[str] = None
