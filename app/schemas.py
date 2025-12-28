from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date

# ---------- AGENT ----------

class AgentCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class AgentResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


# ---------- LEAD ----------

class LeadCreate(BaseModel):
    name: str
    phone_number: Optional[str] = None
    service: Optional[str] = None
    description: Optional[str] = None
    meeting_date: date
    follow_up_date: Optional[date] = None
    agent_ids: List[int]

class LeadUpdate(BaseModel):
    name: Optional[str]
    phone_number: Optional[str]
    service: Optional[str]
    description: Optional[str]
    meeting_date: Optional[date]
    follow_up_date: Optional[date]

class LeadResponse(BaseModel):
    id: int
    name: str
    phone_number: Optional[str]
    service: Optional[str]
    description: Optional[str]
    meeting_date: date
    follow_up_date: Optional[date]
    agent_ids: List[int]
    created_by_id: int

    class Config:
        from_attributes = True
