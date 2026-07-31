from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from contest_rule_guard.db.models import GraphEdgeRow, GraphNodeRow
from contest_rule_guard.graph.models import (
    ConflictReport,
    EdgeRelation,
    GraphEdge,
    GraphNode,
    NodeKind,
    RuleGraph,
)
from contest_rule_guard.rules.models import (
    DeadlineRule,
    RuleStatus,
)
from contest_rule_guard.rules.repository import RuleRepository


class GraphRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def build_graph(self, project_id: UUID) -> RuleGraph:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        rules = RuleRepository(self._session).list_by_project(project_id)

        for rule in rules:
            node = GraphNode(kind=NodeKind.RULE, ref_id=str(rule.id), label=rule.title)
            nodes.append(node)
            for binding in rule.bindings:
                for ev_id in binding.evidence_ids:
                    ev_node = next(
                        (n for n in nodes
                         if n.kind == NodeKind.EVIDENCE
                         and n.ref_id == str(ev_id)),
                        None,
                    )
                    if ev_node is None:
                        ev_node = GraphNode(
                            kind=NodeKind.EVIDENCE, ref_id=str(ev_id), label=f"evidence {ev_id}",
                        )
                        nodes.append(ev_node)
                    edges.append(GraphEdge(
                        relation=EdgeRelation.SUPPORTED_BY,
                        source_id=node.id, target_id=ev_node.id,
                        confirmed=rule.status == RuleStatus.CONFIRMED,
                    ))

            for stage in rule.scope.stages:
                s_node = next(
                    (n for n in nodes if n.kind == NodeKind.STAGE and n.ref_id == stage), None,
                )
                if s_node is None:
                    s_node = GraphNode(kind=NodeKind.STAGE, ref_id=stage, label=stage)
                    nodes.append(s_node)
                edges.append(GraphEdge(
                    relation=EdgeRelation.EXTRACTED_FROM,
                    source_id=node.id, target_id=s_node.id, confirmed=True,
                ))

        # Detect potential conflicts between confirmed rules of same type
        confirmed = [r for r in rules if r.status == RuleStatus.CONFIRMED]
        for i, ra in enumerate(confirmed):
            for rb in confirmed[i + 1:]:
                if (type(ra) is type(rb) and isinstance(ra, DeadlineRule)
                    and isinstance(rb, DeadlineRule) and ra.action == rb.action):
                        edges.append(GraphEdge(
                            relation=EdgeRelation.POTENTIALLY_CONFLICTS,
                            source_id=next(n.id for n in nodes if n.ref_id == str(ra.id)),
                            target_id=next(n.id for n in nodes if n.ref_id == str(rb.id)),
                            confirmed=False,
                        ))

        # Persist
        self._session.query(GraphEdgeRow).filter(
            GraphEdgeRow.id.in_([e.id for e in edges])
        ).delete(synchronize_session="fetch")
        self._session.query(GraphNodeRow).delete(synchronize_session="fetch")
        for node in nodes:
            self._session.add(GraphNodeRow(
                id=node.id, kind=node.kind.value, ref_id=node.ref_id, label=node.label,
            ))
        for edge in edges:
            self._session.add(GraphEdgeRow(
                id=edge.id, relation=edge.relation.value,
                source_id=edge.source_id, target_id=edge.target_id, confirmed=edge.confirmed,
            ))
        self._session.commit()

        return RuleGraph(nodes=nodes, edges=edges)

    def list_conflicts(self, project_id: UUID) -> list[ConflictReport]:
        rules = RuleRepository(self._session).list_by_project(project_id)
        confirmed = [r for r in rules if r.status == RuleStatus.CONFIRMED]
        conflicts: list[ConflictReport] = []
        for i, ra in enumerate(confirmed):
            for rb in confirmed[i + 1:]:
                if (type(ra) is type(rb) and isinstance(ra, DeadlineRule)
                    and isinstance(rb, DeadlineRule) and ra.action == rb.action):
                        conflicts.append(ConflictReport(
                            rule_a_id=ra.id, rule_a_title=ra.title,
                            rule_b_id=rb.id, rule_b_title=rb.title,
                            description=f"Both rules define deadline for action '{ra.action}'",
                        ))
        return conflicts

    def resolve_conflict(
        self, conflict_id: UUID, superseding_rule_id: UUID,
    ) -> ConflictReport | None:
        conflicts = self.list_by_ids(conflict_id)  # Fallback: find in memory
        if conflicts:
            conflict = conflicts[0]
            conflict.resolved = True
            # Mark superseded rule
            other_id = (
                conflict.rule_b_id if superseding_rule_id == conflict.rule_a_id
                else conflict.rule_a_id
            )
            RuleRepository(self._session).update_status(other_id, RuleStatus.SUPERSEDED.value)
            return conflict
        return None

    def list_by_ids(self, *ids: UUID) -> list[ConflictReport]:
        result: list[ConflictReport] = []
        for cid in ids:
            row = self._session.get(GraphNodeRow, cid)
            if row:
                result.append(ConflictReport(
                    id=cid, rule_a_id=uuid4(), rule_a_title="", rule_b_id=uuid4(), rule_b_title="",
                    description="",
                ))
        return result
