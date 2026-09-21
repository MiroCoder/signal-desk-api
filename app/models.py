from sqlalchemy.orm import Mapped, mapped_column
from .database import Base
from sqlalchemy import String

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column()
    priority: Mapped[int] = mapped_column()