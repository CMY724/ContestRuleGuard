"""RuleGraph nodes, edges, and conflict models."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class NodeKind(StrEnum):
    DOCUMENT = "document"
    EVIDENCE = "evidence"
    RULE = "rule"
    STAGE = "stage"
    TRACK = "track"
    ACTION = "action"


class EdgeRelation(StrEnum):
    EXTRACTED_FROM = "extracted_from"
    SUPPORTED_BY = "supported_by"
    SUPERSEDES = "supersedes"
    CONFLICTS_WITH = "conflicts_with"
    DEPENDS_ON = "depends_on"
    POTENTIALLY_CONFLICTS = "potentially_conflicts"
    POTENTIALLY_SUPERSEDES = "potentially_supersedes"


class GraphNode(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    kind: NodeKind
    ref_id: str
    label: str = ""


class GraphEdge(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    relation: EdgeRelation
    source_id: UUID
    target_id: UUID
    confirmed: bool = False


class RuleGraph(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class ConflictReport(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    rule_a_id: UUID
    rule_a_title: str
    rule_b_id: UUID
    rule_b_title: str
    description: str
    resolved: bool = False


class ConflictResolution(BaseModel):
    resolution: str = Field(min_length=1)
    superseding_rule_id: UUID
