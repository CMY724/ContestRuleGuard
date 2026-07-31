export interface RuleCheckResult {
  rule_id: string;
  rule_title: string;
  rule_type: string;
  passed: boolean | null;
  severity: string;
  evidence_quote: string;
  detail: string;
}

export interface ReviewReport {
  project_id: string;
  checked_at: string;
  total_rules: number;
  passed: number;
  failed: number;
  blocked: number;
  results: RuleCheckResult[];
}

export interface GraphNode {
  id: string;
  kind: string;
  ref_id: string;
  label: string;
}

export interface GraphEdge {
  id: string;
  relation: string;
  source_id: string;
  target_id: string;
  confirmed: boolean;
}

export interface RuleGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}
