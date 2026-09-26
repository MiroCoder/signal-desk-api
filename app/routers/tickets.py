from fastapi import APIRouter, HTTPException, Response
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import Ticket, Project, User
from ..schemas import TicketCreate,TicketResponse,TicketUpdate

router = APIRouter()

@router.get("/tickets", response_model=list[TicketResponse])
def get_tickets(priority: int | None = None,
                db: Session = Depends(get_db),
                skip: int = 0,
                limit: int = 10,
                current_user: User = Depends(get_current_user)
                ):
    statement = select(Ticket).join(Project).where(Project.owner_id == current_user.id)
    if priority is not None:
        statement = statement.where(Ticket.priority == priority)
    statement = statement.order_by(Ticket.priority.desc()).offset(skip).limit(limit)
    tickets = db.scalars(statement).all()
    return tickets

@router.patch("/tickets/{ticket_id}", response_model=TicketResponse)
def update_ticket(
        ticket_id: int,
        ticket_update: TicketUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    statement = select(Ticket).join(Project).where(Ticket.id == ticket_id, Project.owner_id == current_user.id)
    db_ticket = db.scalar(statement)
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    update_data = ticket_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_ticket, field, value)

    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@router.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    statement = select(Ticket).join(Project).where(Ticket.id == ticket_id, Project.owner_id == current_user.id)
    db_ticket = db.scalar(statement)
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db.delete(db_ticket)
    db.commit()
    return Response(status_code=204)

@router.post("/tickets", response_model=TicketResponse, status_code=201)
def create_ticket(
        ticket: TicketCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    statement = select(Project).where(Project.id == ticket.project_id, Project.owner_id == current_user.id)
    project = db.scalar(statement)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db_ticket = Ticket(**ticket.model_dump())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)

    return {
        "id": db_ticket.id,
        **ticket.model_dump()
    }

@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int,
               db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)
               ):
    statement = select(Ticket).join(Project).where(Ticket.id == ticket_id, Project.owner_id == current_user.id)
    ticket = db.scalar(statement)

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket