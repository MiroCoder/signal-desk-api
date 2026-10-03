from sqlalchemy.orm import Mapped, mapped_column
from .database import Base
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import relationship
from enum import Enum
from sqlalchemy import Enum as SQLEnum


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column()
    priority: Mapped[int] = mapped_column()
    project_id: Mapped[int ] = mapped_column(
        ForeignKey("projects.id"), nullable=False
    )
    project: Mapped["Project"] = relationship(back_populates="tickets")
    status: Mapped[TicketStatus] = mapped_column(SQLEnum(TicketStatus), default = TicketStatus.OPEN)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="project")
    owner_id: Mapped[int]  = mapped_column(ForeignKey("users.id"), nullable=False)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255),unique=True,index=True)
    hashed_password: Mapped[str] = mapped_column()