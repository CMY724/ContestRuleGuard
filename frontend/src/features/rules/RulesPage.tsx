import { useEffect, useState } from "react";
import { compileRule, listRules, updateRuleStatus } from "./api";
import type { CompilationResult, ContestRule } from "./types";

interface Props {
  projectId: string;
}

const statusLabel: Record<string, string> = {
  needs_review: "待审核",
  confirmed: "已确认",
  rejected: "已拒绝",
  superseded: "已替代",
};

const severityLabel: Record<string, string> = {
  block: "阻塞",
  error: "错误",
  warn: "警告",
  info: "提示",
};

export function RulesPage({ projectId }: Props) {
  const [rules, setRules] = useState<ContestRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [compileResults, setCompileResults] = useState<Record<string, CompilationResult>>({});

  async function load() {
    setLoading(true);
    try {
      setRules(await listRules(projectId));
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [projectId]);

  async function confirm(ruleId: string) {
    await updateRuleStatus(projectId, ruleId, "confirmed");
    await load();
  }

  async function reject(ruleId: string) {
    await updateRuleStatus(projectId, ruleId, "rejected");
    await load();
  }

  async function compile(ruleId: string) {
    try {
      const result = await compileRule(projectId, ruleId);
      setCompileResults((prev) => ({ ...prev, [ruleId]: result }));
    } catch (e) {
      setError(e instanceof Error ? e.message : "编译失败");
    }
  }

  if (loading) return <p>加载规则中...</p>;

  return (
    <section className="rules-page">
      <h2>竞赛规则 ({rules.length})</h2>
      {error && <p className="error" role="alert">{error}</p>}
      {rules.map((rule) => (
        <article key={rule.id} className="rule-card">
          <div className="rule-header">
            <span className="rule-type">{rule.rule_type}</span>
            <h3>{rule.title}</h3>
            <span className={severity severity-}>
              {severityLabel[rule.severity] || rule.severity}
            </span>
            <span className={status status-}>
              {statusLabel[rule.status] || rule.status}
            </span>
          </div>
          <div className="rule-scope">
            阶段: {rule.scope.stages.join(", ")} | 赛道: {rule.scope.tracks.join(", ")}
          </div>
          <div className="rule-detail">
            <pre>{JSON.stringify(rule, null, 2)}</pre>
          </div>
          <div className="rule-bindings">
            <strong>证据引用 ({rule.bindings.length}):</strong>
            {rule.bindings.map((b, i) => (
              <blockquote key={i}>
                <code>{b.field_path}</code>: "{b.quote}"
              </blockquote>
            ))}
          </div>
          {rule.status === "needs_review" && (
            <div className="rule-actions">
              <button className="btn-confirm" onClick={() => confirm(rule.id)}>确认</button>
              <button className="btn-reject" onClick={() => reject(rule.id)}>拒绝</button>
            </div>
          )}
          {rule.status === "confirmed" && (
            <div className="rule-actions">
              <button onClick={() => compile(rule.id)}>编译检查</button>
              {compileResults[rule.id] && (
                <div className="compile-result">
                  <span className={compile-}>
                    {compileResults[rule.id].kind}
                  </span>
                  <pre>{JSON.stringify(compileResults[rule.id].checks, null, 2)}</pre>
                </div>
              )}
            </div>
          )}
        </article>
      ))}
    </section>
  );
}
