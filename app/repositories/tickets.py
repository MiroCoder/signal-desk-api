from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Ticket, Project


def get_owned_ticket(
        db:Session,
        ticket_id:int,
        owner_id:int,
) -> Ticket | None:
    statement = select(Ticket).join(Project).where(Ticket.id == ticket_id, Project.owner_id == owner_id)
    ticket = db.scalar(statement)
    return ticket