from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlalchemy import text

from .database import SessionLocal
from . import models, schemas
from app.security import hash_password, verify_password
from app.auth import create_access_token
from app.dependencies import get_current_agent

app = FastAPI(title="LMS API")

# ---------- CORS ----------
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- DB ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # simple DB ping
        db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "not connected",
            "detail": str(e)
        }


# ---------- AUTH ----------
@app.post("/signup", response_model=schemas.AgentResponse)
def signup(agent: schemas.AgentCreate, db: Session = Depends(get_db)):
    if db.query(models.Agent).filter(models.Agent.email == agent.email).first():
        raise HTTPException(400, "Email already registered")

    db_agent = models.Agent(
        name=agent.name,
        email=agent.email,
        hashed_password=hash_password(agent.password),
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


@app.post("/login")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    agent = db.query(models.Agent).filter(
        models.Agent.email == form.username
    ).first()

    if not agent or not verify_password(form.password, agent.hashed_password):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({"sub": str(agent.id)})
    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ---------- LEADS ----------

@app.post("/leads", response_model=schemas.LeadResponse)
def create_lead(
    lead: schemas.LeadCreate,
    db: Session = Depends(get_db),
    current_agent: models.Agent = Depends(get_current_agent),
):
    db_lead = models.Lead(
        name=lead.name,
        phone_number=lead.phone_number,
        service=lead.service,
        description=lead.description,
        meeting_date=lead.meeting_date,
        follow_up_date=lead.follow_up_date,
        created_by_id=current_agent.id,
    )

    agents = db.query(models.Agent).filter(
        models.Agent.id.in_(lead.agent_ids)
    ).all()

    db_lead.agents = agents

    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)

    return schemas.LeadResponse(
        id=db_lead.id,
        name=db_lead.name,
        phone_number=db_lead.phone_number,
        service=db_lead.service,
        description=db_lead.description,
        meeting_date=db_lead.meeting_date,
        follow_up_date=db_lead.follow_up_date,
        agent_ids=[a.id for a in db_lead.agents],
        created_by_id=db_lead.created_by_id,
    )


@app.get("/leads", response_model=List[schemas.LeadResponse])
def get_all_leads(
    db: Session = Depends(get_db),
    current_agent: models.Agent = Depends(get_current_agent),
):
    leads = db.query(models.Lead).all()

    return [
        schemas.LeadResponse(
            id=l.id,
            name=l.name,
            phone_number=l.phone_number,
            service=l.service,
            description=l.description,
            meeting_date=l.meeting_date,
            follow_up_date=l.follow_up_date,
            agent_ids=[a.id for a in l.agents],
            created_by_id=l.created_by_id,
        )
        for l in leads
    ]


@app.put("/leads/{lead_id}", response_model=schemas.LeadResponse)
def update_lead(
    lead_id: int,
    lead: schemas.LeadUpdate,
    db: Session = Depends(get_db),
    current_agent: models.Agent = Depends(get_current_agent),
):
    db_lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not db_lead:
        raise HTTPException(404, "Lead not found")

    if (
        current_agent.id != db_lead.created_by_id
        and current_agent not in db_lead.agents
    ):
        raise HTTPException(403, "Not allowed")

    for key, value in lead.dict(exclude_unset=True).items():
        setattr(db_lead, key, value)

    db.commit()
    db.refresh(db_lead)

    return schemas.LeadResponse(
        id=db_lead.id,
        name=db_lead.name,
        phone_number=db_lead.phone_number,
        service=db_lead.service,
        description=db_lead.description,
        meeting_date=db_lead.meeting_date,
        follow_up_date=db_lead.follow_up_date,
        agent_ids=[a.id for a in db_lead.agents],
        created_by_id=db_lead.created_by_id,
    )

@app.delete("/leads/{lead_id}", status_code=204)
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_agent: models.Agent = Depends(get_current_agent),
):
    db_lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not db_lead:
        raise HTTPException(404, "Lead not found")

    if current_agent.id != db_lead.created_by_id and current_agent not in db_lead.agents:
        raise HTTPException(403, "Not allowed")

    db.delete(db_lead)
    db.commit()

    return {"message": "Lead deleted successfully"}
