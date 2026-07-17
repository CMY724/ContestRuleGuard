import { ProjectPage } from "./features/projects/ProjectPage";

export default function App() {
  return (
    <main className="app-shell">
      <header>
        <p className="eyebrow">ContestRuleGuard</p>
        <h1>赛规通</h1>
        <p>证据图驱动的竞赛合规智能体</p>
      </header>
      <ProjectPage />
    </main>
  );
}
