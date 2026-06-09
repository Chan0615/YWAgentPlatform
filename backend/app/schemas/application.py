from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    url: str
    icon: Optional[str] = None
    sort_order: int = 0
    status: int = 1


class ApplicationUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None
    status: Optional[int] = None


class ApplicationResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    url: str
    icon: Optional[str] = None
    sort_order: int
    status: int
    created_at: datetime
    updated_at: datetime
    visible_role_ids: List[int] = []

    class Config:
        from_attributes = True


class ApplicationListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[ApplicationResponse]


class AssignApplicationRolesRequest(BaseModel):
    role_ids: List[int]
