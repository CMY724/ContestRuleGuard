from fastapi import Request

from contest_rule_guard.core.config import Settings
from contest_rule_guard.projects.cleanup import (
    FilesystemProjectCleanup,
    ProjectCleanupRegistry,
)


def build_project_cleanup_registry(settings: Settings) -> ProjectCleanupRegistry:
    return ProjectCleanupRegistry(
        FilesystemProjectCleanup(root) for root in settings.project_storage_roots
    )


def get_project_cleanup_registry(request: Request) -> ProjectCleanupRegistry:
    return request.app.state.project_cleanup_registry
