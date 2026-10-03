import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import get_db, Base
from app.main import app

from app.config import settings
from fastapi.testclient import TestClient

from app.models import User, Project, Ticket

password = settings.db_password

TEST_DATABASE_URL = f"postgresql+psycopg://signaldesk_user:{password}@localhost:5432/signaldesk_test"

test_engine = create_engine(TEST_DATABASE_URL)


TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def db_session(setup_database):
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def make_user(db_session):
    def _make_user(email):
        user = User(
            email = email,
            hashed_password = "fake"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _make_user

@pytest.fixture
def make_project(db_session):
    def _make_project(name, owner_id):
        project = Project(
            name = name,
            owner_id = owner_id
        )
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
        return project
    return _make_project

@pytest.fixture
def make_ticket(db_session):
    def _make_ticket(title, description, priority, project_id, status):
        ticket = Ticket(
            title=title,
            description= description,
            priority=priority,
            project_id=project_id,
            status=status
        )
        db_session.add(ticket)
        db_session.commit()
        db_session.refresh(ticket)
        return ticket
    return _make_ticket