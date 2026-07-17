from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from contest_rule_guard.db.models import Project
from contest_rule_guard.db.session import get_session
from contest_rule_guard.projects import repository
from contest_rule_guard.projects.cleanup import ProjectCleanupRegistry
from contest_rule_guard.projects.dependencies import get_project_cleanup_registry
from contest_rule_guard.projects.schemas import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/api/projects", tags=["projects"])
SessionDependency = Annotated[Session, Depends(get_session)]
CleanupDependency = Annotated[
    ProjectCleanupRegistry,
    Depends(get_project_cleanup_registry),
]


def require_project(session: Session, project_id: UUID) -> Project:
    project = repository.get_project(session, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    return project


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create(data: ProjectCreate, session: SessionDependency) -> Project:
    return repository.create_project(session, data)


@router.get("", response_model=list[ProjectRead])
def list_all(session: SessionDependency) -> list[Project]:
    return repository.list_projects(session)


@router.get("/{project_id}", response_model=ProjectRead)
def get_one(project_id: UUID, session: SessionDependency) -> Project:
    return require_project(session, project_id)


@router.patch("/{project_id}", response_model=ProjectRead)
def patch(
    project_id: UUID,
    data: ProjectUpdate,
    session: SessionDependency,
) -> Project:
    return repository.update_project(session, require_project(session, project_id), data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    project_id: UUID,
    session: SessionDependency,
    cleanup: CleanupDependency,
) -> Response:
    project = require_project(session, project_id)
    cleanup.cleanup_project(project.id)
    repository.delete_project(session, project)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
