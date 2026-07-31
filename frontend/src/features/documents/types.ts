export interface BoundingBox {
  left: number;
  top: number;
  right: number;
  bottom: number;
}

export interface TextBlock {
  id: string;
  unit_index: number;
  block_index: number;
  source_path: string;
  text: string;
  kind: string;
  bbox: BoundingBox | null;
  confidence: number;
  needs_review: boolean;
}

export interface DocumentUnit {
  index: number;
  kind: string;
  width: number | null;
  height: number | null;
  blocks: TextBlock[];
}

export interface NormalizedDocument {
  id: string;
  filename: string;
  media_type: string;
  content_sha256: string;
  source_tier: string;
  stage: string;
  units: DocumentUnit[];
}

export interface EvidenceSpan {
  id: string;
  document_id: string;
  block_id: string;
  field_path: string;
  quote: string;
  start_char: number;
  end_char: number;
  source_tier: string;
  stage: string;
  document_sha256: string;
}
