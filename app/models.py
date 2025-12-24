from sqlalchemy import Column, Integer, String, Text, Date, Table, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

agent_leads = Table(
    "agent_leads",
    Base.metadata,
    Column("agent_id", ForeignKey("agents.id"), primary_key=True),
    Column("lead_id", ForeignKey("leads.id"), primary_key=True),
)

class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    leads = relationship("Lead", secondary=agent_leads, back_populates="agents")

class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    service = Column(String(100))
    description = Column(Text)
    meeting_date = Column(Date)
    follow_up_date = Column(Date)

    agents = relationship("Agent", secondary=agent_leads, back_populates="leads")
