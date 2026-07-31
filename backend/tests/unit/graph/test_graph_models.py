from contest_rule_guard.graph.models import (
    ConflictReport,
    EdgeRelation,
    GraphEdge,
    GraphNode,
    NodeKind,
    RuleGraph,
)


def test_graph_node_creation() -> None:
    node = GraphNode(kind=NodeKind.RULE, ref_id="rule-1", label="Deadline Rule")
    assert node.kind == NodeKind.RULE
    assert node.ref_id == "rule-1"


def test_graph_edge_confirmed_defaults_false() -> None:
    edge = GraphEdge(
        relation=EdgeRelation.SUPPORTED_BY,
        source_id=GraphNode(kind=NodeKind.RULE, ref_id="r1").id,
        target_id=GraphNode(kind=NodeKind.EVIDENCE, ref_id="e1").id,
    )
    assert edge.confirmed is False


def test_rule_graph_empty_by_default() -> None:
    g = RuleGraph()
    assert g.nodes == []
    assert g.edges == []


def test_conflict_report() -> None:
    from uuid import uuid4
    a, b = uuid4(), uuid4()
    c = ConflictReport(
        rule_a_id=a, rule_a_title="Deadline A",
        rule_b_id=b, rule_b_title="Deadline B",
        description="conflict",
    )
    assert c.resolved is False
