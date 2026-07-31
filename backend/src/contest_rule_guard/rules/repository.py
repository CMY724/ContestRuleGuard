from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from contest_rule_guard.db.models import ContestRuleRow
from contest_rule_guard.rules.models import ContestRule, ContestRuleAdapter


class RuleRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, project_id: UUID, rule: ContestRule) -> ContestRule:
        row = ContestRuleRow(
            id=rule.id,
            project_id=project_id,
            rule_type=rule.rule_type,
            title=rule.title,
            scope_json=rule.scope.model_dump_json(),
            severity=rule.severity.value,
            status=rule.status.value,
            confidence=rule.confidence,
            payload_json=rule.model_dump_json(
                exclude={"id", "rule_type", "title", "scope",
                         "severity", "status", "confidence",
                         "bindings", "notes"},
            ),
            bindings_json=rule.model_dump_json(include={"bindings"}),
            notes=rule.notes,
        )
        self._session.add(row)
        self._session.commit()
        return rule

    def list_by_project(self, project_id: UUID) -> list[ContestRule]:
        statement = select(ContestRuleRow).where(
            ContestRuleRow.project_id == project_id,
        )
        rows = self._session.scalars(statement).all()
        return [self._to_domain(row) for row in rows]

    def get(self, rule_id: UUID) -> ContestRule | None:
        row = self._session.get(ContestRuleRow, rule_id)
        return self._to_domain(row) if row else None

    def update_status(self, rule_id: UUID, status: str) -> ContestRule | None:
        row = self._session.get(ContestRuleRow, rule_id)
        if row is None:
            return None
        row.status = status
        self._session.commit()
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: ContestRuleRow) -> ContestRule:
        import json
        payload = json.loads(row.payload_json)
        bindings_data = json.loads(row.bindings_json)
        scope_data = json.loads(row.scope_json)
        data = {
            "id": str(row.id),
            "rule_type": row.rule_type,
            "title": row.title,
            "scope": scope_data,
            "severity": row.severity,
            "status": row.status,
            "confidence": row.confidence,
            "bindings": bindings_data.get("bindings", []),
            "notes": row.notes or "",
            **payload,
        }
        return ContestRuleAdapter.validate_python(data)
