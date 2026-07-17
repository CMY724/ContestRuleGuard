from typing import Protocol
from uuid import UUID

from contest_rule_guard.projects.models import ProjectDiscoveryContext


class ProjectReadPort(Protocol):
    def get_public_discovery_context(self, project_id: UUID) -> ProjectDiscoveryContext: ...
