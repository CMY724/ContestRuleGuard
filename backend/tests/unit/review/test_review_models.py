from uuid import uuid4

from contest_rule_guard.review.models import ReviewReport, RuleCheckResult


def test_review_report_pass_rate() -> None:
    report = ReviewReport(project_id=uuid4(), total_rules=4, passed=3, failed=1)
    assert report.pass_rate == 0.75


def test_review_report_zero_rules() -> None:
    report = ReviewReport(project_id=uuid4())
    assert report.pass_rate == 0.0


def test_rule_check_result_defaults() -> None:
    r = RuleCheckResult(rule_id=uuid4(), rule_title="test", rule_type="deadline")
    assert r.passed is None
    assert r.severity == "warn"
    assert r.blocked_reason == ""
