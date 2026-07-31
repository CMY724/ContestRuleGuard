"""HTML report generator for review results."""

from contest_rule_guard.review.models import ReviewReport


def export_html(report: ReviewReport, project_name: str = "") -> str:
    """Generate a self-contained HTML compliance report."""
    passed_pct = round(report.pass_rate * 100, 1)
    results_html = ""
    for r in report.results:
        if r.passed is True:
            icon, cls = "✓", "pass"
        elif r.passed is False:
            icon, cls = "✗", "fail"
        else:
            icon, cls = "⊘", "blocked"
        results_html += f"""<tr class="{cls}">
            <td>{icon}</td>
            <td><code>{r.rule_type}</code></td>
            <td>{r.rule_title}</td>
            <td>{r.severity}</td>
            <td>{r.evidence_quote[:120]}</td>
            <td>{r.blocked_reason or r.detail[:200]}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>赛规通 · 合规审查报告</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 960px; margin: 0 auto; padding: 2rem; }}
h1 {{ border-bottom: 2px solid #2563eb; padding-bottom: 0.5rem; }}
.stats {{ display: flex; gap: 2rem; margin: 1.5rem 0; }}
.stat {{ text-align: center; padding: 1rem; border-radius: 8px; background: #f8fafc; min-width: 100px; }}
.stat .num {{ font-size: 2rem; font-weight: bold; }}
.stat .label {{ color: #64748b; font-size: 0.85rem; }}
.pass .num {{ color: #16a34a; }}
.fail .num {{ color: #dc2626; }}
.blocked .num {{ color: #d97706; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
th, td {{ padding: 0.5rem 0.75rem; text-align: left; border-bottom: 1px solid #e2e8f0; }}
th {{ background: #f1f5f9; }}
tr.pass {{ background: #f0fdf4; }}
tr.fail {{ background: #fef2f2; }}
tr.blocked {{ background: #fffbeb; }}
footer {{ margin-top: 2rem; color: #94a3b8; font-size: 0.8rem; text-align: center; }}
</style>
</head>
<body>
<h1>赛规通 · 合规审查报告</h1>
<p>项目: {project_name or report.project_id} | 检查时间: {report.checked_at.strftime('%Y-%m-%d %H:%M UTC')}</p>
<div class="stats">
    <div class="stat"><div class="num">{report.total_rules}</div><div class="label">总规则数</div></div>
    <div class="stat pass"><div class="num">{report.passed}</div><div class="label">通过</div></div>
    <div class="stat fail"><div class="num">{report.failed}</div><div class="label">未通过</div></div>
    <div class="stat blocked"><div class="num">{report.blocked}</div><div class="label">阻塞</div></div>
    <div class="stat"><div class="num">{passed_pct}%</div><div class="label">通过率</div></div>
</div>
<table>
<thead><tr><th></th><th>类型</th><th>规则</th><th>严重性</th><th>证据</th><th>详情</th></tr></thead>
<tbody>{results_html}</tbody>
</table>
<footer>ContestRuleGuard 赛规通 · 证据图驱动的竞赛合规智能体</footer>
</body>
</html>"""
