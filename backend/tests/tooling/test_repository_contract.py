from pathlib import Path

ROOT = Path(__file__).parents[3]


def test_local_and_ci_validation_cover_every_quality_gate() -> None:
    local = (ROOT / "scripts" / "verify.ps1").read_text(encoding="utf-8")
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    local_required = [
        "'ruff', 'check', 'backend'",
        "'mypy', 'backend/src'",
        "'pytest', 'backend/tests', '-q'",
        "'--dir', 'frontend', 'lint'",
        "'--dir', 'frontend', 'test', '--run'",
        "'--dir', 'frontend', 'build'",
    ]
    ci_required = [
        "ruff check backend",
        "mypy backend/src",
        "pytest backend/tests -q",
        "--dir frontend lint",
        "--dir frontend test --run",
        "--dir frontend build",
    ]
    for command in local_required:
        assert command in local
    for command in ci_required:
        assert command in ci
