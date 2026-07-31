import { useState, type FormEvent } from "react";
import { uploadDocument } from "./api";
import type { NormalizedDocument } from "./types";

interface Props {
  projectId: string;
  onUploaded: (doc: NormalizedDocument) => void;
}

export function DocumentUpload({ projectId, onUploaded }: Props) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setUploading(true);
    setError("");
    const form = e.currentTarget;
    const values = new FormData(form);
    const file = values.get("file") as File;
    if (!file) {
      setError("请选择文件");
      setUploading(false);
      return;
    }
    try {
      const doc = await uploadDocument(
        projectId,
        file,
        String(values.get("source_tier") || "primary"),
        String(values.get("stage") || "school"),
      );
      onUploaded(doc);
      form.reset();
    } catch (err) {
      setError(err instanceof Error ? err.message : "上传失败");
    } finally {
      setUploading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="upload-form">
      <h3>上传规则文档</h3>
      {error && <p className="error" role="alert">{error}</p>}
      <label>
        文档类型
        <select name="source_tier" defaultValue="primary">
          <option value="primary">一级来源（官方通知）</option>
          <option value="secondary">二级来源（院系转发）</option>
          <option value="auxiliary">辅助来源（参赛指南）</option>
        </select>
      </label>
      <label>
        比赛阶段
        <select name="stage" defaultValue="school">
          <option value="school">校赛</option>
          <option value="provincial">省赛</option>
          <option value="national">国赛</option>
        </select>
      </label>
      <label>
        选择文件（PDF/DOCX/PPTX/HTML/图片）
        <input type="file" name="file" accept=".pdf,.docx,.pptx,.html,.htm,.png,.jpg,.jpeg,.webp,.bmp" required />
      </label>
      <button disabled={uploading}>
        {uploading ? "上传解析中..." : "上传并解析"}
      </button>
    </form>
  );
}
