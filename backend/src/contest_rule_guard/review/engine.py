"""Review engine: compile confirmed rules and check against facts."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from contest_rule_guard.review.models import ReviewReport, RuleCheckResult
from contest_rule_guard.rules.compiler import CompilationKind, compile_rule
from contest_rule_guard.rules.models import (
    RuleStatus,
)
from contest_rule_guard.rules.repository import RuleRepository


class ReviewEngine:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repo = RuleRepository(session)

    def review(self, project_id: UUID, facts: dict | None = None) -> ReviewReport:
        rules = self._repo.list_by_project(project_id)
        report = ReviewReport(project_id=project_id, total_rules=len(rules))

        now = datetime.now(UTC).isoformat()
        default_facts = facts or {"current_time": now}

        for rule in rules:
            result = RuleCheckResult(
                rule_id=rule.id,
                rule_title=rule.title,
                rule_type=rule.rule_type,
                severity=rule.severity.value,
            )

            if rule.status != RuleStatus.CONFIRMED:
                result.passed = None
                result.blocked_reason = f"rule status is {rule.status.value}, not confirmed"
                report.blocked += 1
                report.results.append(result)
                continue

            compilation = compile_rule(rule, default_facts)

            if compilation.kind == CompilationKind.BLOCKED:
                result.passed = None
                result.blocked_reason = "compilation blocked"
                report.blocked += 1
            elif compilation.kind == CompilationKind.MISSING_FACTS:
                result.passed = None
                result.blocked_reason = "missing facts for execution"
                report.blocked += 1
            else:
                # Check if all checks passed
                all_passed = all(
                    c.get("_passed", True) for c in compilation.checks
                )
                result.passed = all_passed
                if all_passed:
                    report.passed += 1
                else:
                    report.failed += 1
                    failed_checks = [c for c in compilation.checks if not c.get("_passed", True)]
                    result.detail = str(failed_checks)

            # Gather evidence quotes
            quotes = []
            for binding in rule.bindings:
                quotes.append(binding.quote)
            result.evidence_quote = "; ".join(quotes[:3])

            report.results.append(result)

        return report
