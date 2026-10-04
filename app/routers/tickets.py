from fastapi import APIRouter, HTTPException, Response
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..dependencies import get_current_user
from ..models import Ticket, Project, User, TicketStatus
from ..schemas import TicketCreate, TicketResponse, TicketUpdate, TicketUpdateStatus
from ..services.tickets import is_status_transition_allowed
from ..repositories.tickets import get_owned_ticket

router = APIRouter()


def get_owned_ticket_or_404(
        db: Session,
        ticket_id: int,
        owner_id: int,
) -> Ticket:
    ticket = get_owned_ticket(db, ticket_id, owner_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="No ticket found.")
    return ticket


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
    db_ticket = get_owned_ticket_or_404(db, ticket_id, current_user.id)

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
    ticket = get_owned_ticket_or_404(db, ticket_id, current_user.id)

    db.delete(ticket)
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
        "status": db_ticket.status,
        **ticket.model_dump()
    }


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int,
               db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)
               ):
    ticket = get_owned_ticket_or_404(
        db,
        ticket_id,
        current_user.id
    )
    return ticket


@router.patch("/tickets/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status(ticket_id: int, update: TicketUpdateStatus, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    ticket = get_owned_ticket_or_404(db, ticket_id, current_user.id)

    if not is_status_transition_allowed(ticket.status, update.status):
        raise HTTPException(status_code=409, detail="Not allowed")

    ticket.status = update.status
    db.commit()
    db.refresh(ticket)

    return ticket
