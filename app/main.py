from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi import Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import Ticket

app = FastAPI()

class TicketCreate(BaseModel):
    title: str = Field (min_length=3)
    description: str
    priority: int = Field(ge=1,le=5)

class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: int

@app.post("/tickets", response_model=TicketResponse, status_code =201)
def create_ticket(
        ticket: TicketCreate,
        db: Session = Depends(get_db)
    ):
    db_ticket = Ticket(**ticket.model_dump())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return {
        "id": db_ticket.id,
        **ticket.model_dump()
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}

@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int):
    if ticket_id >100:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"ticket_id": ticket_id, "title": "Test ticket"}

@app.get("/tickets")
def get_tickets(priority: int | None = None):
    return {"priority": priority}