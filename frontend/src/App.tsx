import { useState } from "react";
import { ProjectPage } from "./features/projects/ProjectPage";
import { DocumentsPage } from "./features/documents/DocumentsPage";
import { RulesPage } from "./features/rules/RulesPage";
import { ReviewPage } from "./features/review/ReviewPage";

type Tab = "projects" | "documents" | "rules" | "review";

export default function App() {
  const [tab, setTab] = useState<Tab>("projects");
  const [activeProjectId, setActiveProjectId] = useState<string | null>(null);

  return (
    <main className="app-shell">
      <header>
        <p className="eyebrow">ContestRuleGuard</p>
        <h1>赛规通</h1>
        <p>证据图驱动的竞赛合规智能体</p>
        <nav className="tab-nav">
          <button
            className={tab === "projects" ? "active" : ""}
            onClick={() => setTab("projects")}
          >
            项目管理
          </button>
          <button
            className={tab === "documents" ? "active" : ""}
            onClick={() => setTab("documents")}
            disabled={!activeProjectId}
          >
            规则文档
          </button>
          <button
            className={tab === "rules" ? "active" : ""}
            onClick={() => setTab("rules")}
            disabled={!activeProjectId}
          >
            规则管理
          </button>
          <button
            className={tab === "review" ? "active" : ""}
            onClick={() => setTab("review")}
            disabled={!activeProjectId}
          >
            合规审查
          </button>
        </nav>
      </header>
      {tab === "projects" && (
        <ProjectPage onSelectProject={setActiveProjectId} />
      )}
      {tab === "documents" && activeProjectId && (
        <DocumentsPage projectId={activeProjectId} />
      )}
      {tab === "rules" && activeProjectId && (
        <RulesPage projectId={activeProjectId} />
      )}
      {tab === "review" && activeProjectId && (
        <ReviewPage projectId={activeProjectId} />
      )}
    </main>
  );
}
