from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from contest_rule_guard.db.models import Project
from contest_rule_guard.projects.schemas import ProjectCreate, ProjectUpdate


def create_project(session: Session, data: ProjectCreate) -> Project:
    project = Project(**data.model_dump())
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def list_projects(session: Session) -> list[Project]:
    statement = select(Project).order_by(Project.created_at.desc(), Project.id)
    return list(session.scalars(statement))


def get_project(session: Session, project_id: UUID) -> Project | None:
    return session.get(Project, project_id)


def update_project(session: Session, project: Project, data: ProjectUpdate) -> Project:
    for field, value in data.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(project, field, value)
    session.commit()
    session.refresh(project)
    return project


def delete_project(session: Session, project: Project) -> None:
    session.delete(project)
    session.commit()
