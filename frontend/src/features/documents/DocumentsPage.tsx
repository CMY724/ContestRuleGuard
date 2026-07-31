import { useEffect, useState } from "react";
import { DocumentUpload } from "./DocumentUpload";
import { listDocuments } from "./api";
import type { NormalizedDocument } from "./types";

interface Props {
  projectId: string;
}

export function DocumentsPage({ projectId }: Props) {
  const [docs, setDocs] = useState<NormalizedDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<NormalizedDocument | null>(null);

  useEffect(() => {
    listDocuments(projectId)
      .then(setDocs)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [projectId]);

  return (
    <section className="documents-page">
      <h2>规则文档</h2>
      <DocumentUpload
        projectId={projectId}
        onUploaded={(doc) => setDocs((prev) => [doc, ...prev])}
      />
      {loading && <p>加载中...</p>}
      {error && <p className="error" role="alert">{error}</p>}
      <div className="doc-list">
        {docs.map((doc) => (
          <article
            key={doc.id}
            className={doc-card }
            onClick={() => setSelected(doc)}
          >
            <h4>{doc.filename}</h4>
            <span className="badge">{doc.source_tier}</span>
            <span className="badge">{doc.stage}</span>
            <p>{doc.units.length} 个单元, {doc.units.reduce((s, u) => s + u.blocks.length, 0)} 个文本块</p>
          </article>
        ))}
      </div>
      {selected && (
        <div className="doc-detail">
          <h3>{selected.filename}</h3>
          {selected.units.map((unit) => (
            <div key={unit.index}>
              <h4>单元 {unit.index} ({unit.kind})</h4>
              {unit.blocks.map((block) => (
                <div key={block.id} className="block">
                  <span className="block-path">{block.source_path}</span>
                  <p>{block.text}</p>
                  {block.needs_review && <span className="warn">需要人工审核</span>}
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
