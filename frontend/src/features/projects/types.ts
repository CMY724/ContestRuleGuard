export type TargetStage = "school" | "provincial" | "national";

export interface ProjectCreate {
  name: string;
  competition_name: string;
  competition_year: number;
  track: string;
  target_stage: TargetStage;
}

export interface Project extends ProjectCreate {
  id: string;
  created_at: string;
  updated_at: string;
}
