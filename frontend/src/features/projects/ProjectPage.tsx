import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { createProject, listProjects } from "./api";
import type { Project, ProjectCreate, TargetStage } from "./types";


const stageNames: Record<TargetStage, string> = {
  school: "校赛",
  provincial: "省赛",
  national: "国赛",
};

export function ProjectPage({ onSelectProject }: { onSelectProject: (id: string) => void }) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    listProjects()
      .then((loadedProjects) => {
        if (active) {
          setProjects(loadedProjects);
        }
      })
      .catch((reason: Error) => {
        if (active) {
          setError(reason.message);
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    const form = event.currentTarget;
    const values = new FormData(form);
    const payload: ProjectCreate = {
      name: String(values.get("name")),
      competition_name: String(values.get("competition_name")),
      competition_year: Number(values.get("competition_year")),
      track: String(values.get("track")),
      target_stage: String(values.get("target_stage")) as TargetStage,
    };
    try {
      const created = await createProject(payload);
      setProjects((current) => [created, ...current]);
      form.reset();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "创建失败");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="project-layout">
      <form className="project-form" onSubmit={submit}>
        <h2>创建竞赛项目</h2>
        <label>
          项目名称
          <input name="name" aria-label="项目名称" required />
        </label>
        <label>
          比赛名称
          <input name="competition_name" aria-label="比赛名称" required />
        </label>
        <label>
          比赛年份
          <input
            name="competition_year"
            aria-label="比赛年份"
            type="number"
            min="2000"
            max="2100"
            defaultValue="2026"
            required
          />
        </label>
        <label>
          参赛赛道
          <input name="track" aria-label="参赛赛道" required />
        </label>
        <label>
          目标阶段
          <select
            name="target_stage"
            aria-label="目标阶段"
            defaultValue="school"
          >
            <option value="school">校赛</option>
            <option value="provincial">省赛</option>
            <option value="national">国赛</option>
          </select>
        </label>
        <button disabled={loading || submitting}>
          {submitting ? "创建中�? : "创建项目"}
        </button>
      </form>

      <div className="project-list">
        <h2>竞赛项目</h2>
        {loading && <p>正在加载�?/p>}
        {!loading && !error && projects.length === 0 && <p>还没有项�?/p>}
        {error && <p role="alert">{error}</p>}
        {projects.map((project) => (
          <article className="project-card" key={project.id} onClick={() => onSelectProject(project.id)} style={{cursor:"pointer"}}>
            <h3>{project.name}</h3>
            <p>
              {project.competition_year} · {project.track} ·{" "}
              {stageNames[project.target_stage]}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}
