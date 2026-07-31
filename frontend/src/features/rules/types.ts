export interface RuleScope {
  stages: string[];
  tracks: string[];
  artifact_kinds: string[];
}

export interface FieldEvidenceBinding {
  field_path: string;
  evidence_ids: string[];
  quote: string;
}

export interface BaseRule {
  id: string;
  rule_type: string;
  title: string;
  scope: RuleScope;
  severity: string;
  status: string;
  confidence: number;
  bindings: FieldEvidenceBinding[];
  notes: string;
}

export interface DeadlineRule extends BaseRule {
  rule_type: "deadline";
  action: string;
  due_at: string;
  timezone: string;
  inclusive: boolean;
}

export interface EligibilityRule extends BaseRule {
  rule_type: "eligibility";
  condition: string;
  qualification: string;
}

export interface TeamSizeRule extends BaseRule {
  rule_type: "team_size";
  min_members: number;
  max_members: number;
  advisor_required: boolean;
}

export interface FileRequiredRule extends BaseRule {
  rule_type: "file_required";
  file_name_pattern: string;
  description: string;
  mandatory: boolean;
}

export interface FileConstraintRule extends BaseRule {
  rule_type: "file_constraint";
  file_name_pattern: string;
  max_size_bytes: number | null;
  allowed_formats: string[];
  page_limit: number | null;
}

export interface ConsistencyRule extends BaseRule {
  rule_type: "consistency";
  left_field: string;
  right_field: string;
  relation: string;
}

export interface AnonymityRule extends BaseRule {
  rule_type: "anonymity";
  prohibited_patterns: string[];
}

export interface DependencyRule extends BaseRule {
  rule_type: "dependency";
  depends_on_rule_id: string;
  dependency_type: string;
}

export type ContestRule =
  | DeadlineRule
  | EligibilityRule
  | TeamSizeRule
  | FileRequiredRule
  | FileConstraintRule
  | ConsistencyRule
  | AnonymityRule
  | DependencyRule;

export interface CompilationResult {
  kind: string;
  rule_id: string;
  checks: Record<string, unknown>[];
}
