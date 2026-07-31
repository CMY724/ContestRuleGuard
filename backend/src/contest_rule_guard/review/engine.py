"""Review engine: compile confirmed rules and check against facts."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from contest_rule_guard.review.facts import SubmissionFacts
from contest_rule_guard.review.models import ReviewReport, RuleCheckResult
from contest_rule_guard.rules.compiler import CompilationKind, compile_rule
from contest_rule_guard.rules.models import RuleStatus
from contest_rule_guard.rules.repository import RuleRepository


class ReviewEngine:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repo = RuleRepository(session)

    def review(
        self, project_id: UUID, facts: SubmissionFacts | None = None
    ) -> ReviewReport:
        rules = self._repo.list_by_project(project_id)
        report = ReviewReport(project_id=project_id, total_rules=len(rules))

        if facts is None:
            facts = SubmissionFacts(current_time=datetime.now(UTC))

        # Build rule_results from this review pass
        rule_results: dict[str, bool] = {}

        for rule in rules:
            result = RuleCheckResult(
                rule_id=rule.id,
                rule_title=rule.title,
                rule_type=rule.rule_type,
                severity=rule.severity.value,
            )

            if rule.status != RuleStatus.CONFIRMED:
                result.passed = None
                result.blocked_reason = (
                    f"rule status is {rule.status.value}, not confirmed"
                )
                report.blocked += 1
                report.results.append(result)
                continue

            # Inject current rule_results for DependencyRule
            enriched = facts.model_copy(update={"rule_results": rule_results})
            compilation = compile_rule(rule, enriched)

            if compilation.kind == CompilationKind.BLOCKED:
                result.passed = None
                result.blocked_reason = "compilation blocked"
                report.blocked += 1
            elif compilation.kind == CompilationKind.MISSING_FACTS:
                result.passed = None
                result.blocked_reason = "missing facts for execution"
                report.blocked += 1
            else:
                all_passed = all(
                    c.get("_passed", True) for c in compilation.checks
                )
                result.passed = all_passed
                if all_passed:
                    report.passed += 1
                else:
                    report.failed += 1
                    failed_checks = [
                        c for c in compilation.checks
                        if not c.get("_passed", True)
                    ]
                    result.detail = str(failed_checks)

                # Record for DependencyRule
                rule_results[str(rule.id)] = all_passed

            # Gather evidence quotes
            quotes = []
            for binding in rule.bindings:
                quotes.append(binding.quote)
            result.evidence_quote = "; ".join(quotes[:3])

            report.results.append(result)

        return report
