from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# ---------- AGENT ----------

class AgentCreate(BaseModel):
    name: str

class AgentResponse(AgentCreate):
    id: int

    class Config:
        from_attributes = True


# ---------- LEAD ----------

class LeadCreate(BaseModel):
    name: str
    service: Optional[str] = None
    description: Optional[str] = None
    meeting_date: date
    follow_up_date: Optional[date] = None
    agent_ids: List[int]


class LeadResponse(BaseModel):
    id: int
    name: str
    service: Optional[str]
    description: Optional[str]
    meeting_date: date
    follow_up_date: Optional[date]
    agent_ids: List[int]

    class Config:
        from_attributes = True
