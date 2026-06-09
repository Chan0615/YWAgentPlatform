from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class PermissionCreate(BaseModel):
    parent_id: Optional[int] = None
    name: str
    code: str
    type: str  # app, menu, button
    path: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int = 0
    status: int = 1


class PermissionUpdate(BaseModel):
    parent_id: Optional[int] = None
    name: Optional[str] = None
    code: Optional[str] = None
    type: Optional[str] = None
    path: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None
    status: Optional[int] = None


class PermissionResponse(BaseModel):
    id: int
    parent_id: Optional[int] = None
    name: str
    code: str
    type: str
    path: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int
    status: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PermissionTreeResponse(BaseModel):
    id: int
    parent_id: Optional[int] = None
    name: str
    code: str
    type: str
    path: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int
    status: int
    created_at: datetime
    updated_at: datetime
    children: List["PermissionTreeResponse"] = []

    class Config:
        from_attributes = True


# Rebuild model for self-referencing
PermissionTreeResponse.model_rebuild()
