from datetime import datetime
from typing import Optional

class UserDTO:
    def __init__(
        self,
        username: str,
        email: str,
        is_active: bool = True,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None
    ):
        self.id = id
        self.username = username
        self.email = email
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
        self.last_login = last_login

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

class CredentialsDTO:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        
    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password
        }