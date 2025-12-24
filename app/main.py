from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .database import engine, SessionLocal, Base
from . import models, schemas

app = FastAPI(title="LMS API")



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/agents", response_model=schemas.AgentResponse)
def create_agent(agent: schemas.AgentCreate, db: Session = Depends(get_db)):
    db_agent = models.Agent(**agent.dict())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


@app.post("/leads", response_model=schemas.LeadResponse)
def create_lead(lead: schemas.LeadCreate, db: Session = Depends(get_db)):

    db_lead = models.Lead(
        name=lead.name,
        service=lead.service,
        description=lead.description,
        meeting_date=lead.meeting_date,
        follow_up_date=lead.follow_up_date,
    )

    agents = db.query(models.Agent).filter(
        models.Agent.id.in_(lead.agent_ids)
    ).all()

    db_lead.agents = agents

    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)

    # 🔥 MANUAL RESPONSE SHAPING
    return schemas.LeadResponse(
        id=db_lead.id,
        name=db_lead.name,
        service=db_lead.service,
        description=db_lead.description,
        meeting_date=db_lead.meeting_date,
        follow_up_date=db_lead.follow_up_date,
        agent_ids=[agent.id for agent in db_lead.agents],
    )
