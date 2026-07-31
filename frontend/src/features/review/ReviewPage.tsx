import { useState } from "react";
import { runReview } from "./api";
import type { ReviewReport } from "./types";

interface Props {
  projectId: string;
}

const statusLabel: Record<string, string> = {
  needs_review: "待审核",
  confirmed: "已确认",
  rejected: "已拒绝",
  superseded: "已替代",
};

export function ReviewPage({ projectId }: Props) {
  const [report, setReport] = useState<ReviewReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [facts, setFacts] = useState("");
  // Removed unused state; using local variable for reportUrl

  async function handleReview() {
    setLoading(true);
    setError("");
    try {
      let factsObj: Record<string, unknown> | undefined;
      if (facts.trim()) {
        factsObj = JSON.parse(facts);
      }
      const result = await runReview(projectId, factsObj);
      setReport(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "审查失败");
    } finally {
      setLoading(false);
    }
  }

  const reportUrl = `/api/projects/${projectId}/review/report`;

  return (
    <section className="review-page">
      <h2>合规审查</h2>

      <div className="review-controls">
        <label>
          手动补充事实 (JSON, 可选):
          <textarea
            rows={4}
            value={facts}
            onChange={(e) => setFacts(e.target.value)}
            placeholder='{"team_member_count": 3, "eligibility_met": true}'
          />
        </label>
        <button onClick={handleReview} disabled={loading}>
          {loading ? "审查中..." : "运行审查"}
        </button>
      </div>

      {error && <p className="error" role="alert">{error}</p>}

      {report && (
        <div className="review-report">
          <div className="report-summary">
            <span className="stat">总规则: {report.total_rules}</span>
            <span className="stat pass">通过: {report.passed}</span>
            <span className="stat fail">失败: {report.failed}</span>
            <span className="stat blocked">阻塞: {report.blocked}</span>
            <span className="stat">
              通过率:{" "}
              {report.total_rules > 0
                ? ((report.passed / report.total_rules) * 100).toFixed(1) + "%"
                : "N/A"}
            </span>
          </div>

          <p>
            <a href={reportUrl} target="_blank" rel="noreferrer">
              下载 HTML 报告
            </a>
          </p>

          <h3>详细结果</h3>
          {report.results.map((r) => (
            <article
              key={r.rule_id}
              className={`rule-result ${
                r.passed === true ? "pass" : r.passed === false ? "fail" : "blocked"
              }`}
            >
              <div className="result-header">
                <span className="rule-type">{r.rule_type}</span>
                <strong>{r.rule_title}</strong>
                <span
                  className={`badge ${
                    r.passed === true
                      ? "badge-pass"
                      : r.passed === false
                        ? "badge-fail"
                        : "badge-blocked"
                  }`}
                >
                  {r.passed === true
                    ? "PASS"
                    : r.passed === false
                      ? "FAIL"
                      : "BLOCKED"}
                </span>
              </div>
              {r.evidence_quote && (
                <blockquote>证据: "{r.evidence_quote}"</blockquote>
              )}
              {r.detail && (
                <details>
                  <summary>详情</summary>
                  <pre>{r.detail}</pre>
                </details>
              )}
              {r.blocked_reason && (
                <p className="blocked-reason">阻塞原因: {r.blocked_reason}</p>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
