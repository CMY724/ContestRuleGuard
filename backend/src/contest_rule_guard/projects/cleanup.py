import shutil
from collections.abc import Iterable
from pathlib import Path
from typing import Protocol
from uuid import UUID


class ProjectCleanupPort(Protocol):
    def cleanup_project(self, project_id: UUID) -> None: ...


class ProjectCleanupRegistry:
    def __init__(self, cleaners: Iterable[ProjectCleanupPort] = ()) -> None:
        self._cleaners = list(cleaners)

    def register(self, cleaner: ProjectCleanupPort) -> None:
        self._cleaners.append(cleaner)

    def cleanup_project(self, project_id: UUID) -> None:
        for cleaner in self._cleaners:
            cleaner.cleanup_project(project_id)


class FilesystemProjectCleanup:
    def __init__(self, root: Path) -> None:
        self._root = root

    def cleanup_project(self, project_id: UUID) -> None:
        root = self._root.resolve()
        target = (root / str(project_id)).resolve()
        if target.parent != root:
            raise ValueError("project storage path escaped configured root")
        if target.exists():
            shutil.rmtree(target)
