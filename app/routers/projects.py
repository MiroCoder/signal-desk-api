from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import Project, User
from ..schemas import ProjectCreate,ProjectResponse,ProjectUpdate

router = APIRouter()

@router.post("/projects", response_model=ProjectResponse,
          status_code=201)
def create_project(project: ProjectCreate,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    db_project = Project(
        name=project.name,
        owner_id=current_user.id
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/projects", response_model=list[ProjectResponse])
def get_projects(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    statement = select(Project).where(Project.owner_id == current_user.id)
    projects = db.scalars(statement).all()
    return projects


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
        project_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    statement = select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)
    project = db.scalar(statement)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.patch("/projects/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int,
                   project_update: ProjectUpdate,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    statement = select(Project).where(Project.id==project_id,Project.owner_id == current_user.id)
    project = db.scalar(statement)
    if project is None:
        raise HTTPException(status_code=404,detail="Project not found")

    update_data = project_update.model_dump(exclude_unset=True)

    for field,value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)

    return project