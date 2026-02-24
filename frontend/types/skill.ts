export interface Skill {
  id: string;
  user_id: string;
  name: string;
  slug: string;
  description: string | null;
  version: number;
  is_public: boolean;
  tree_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface SkillListResponse {
  items: Skill[];
  total: number;
}

export interface CreateSkillRequest {
  name: string;
  slug: string;
  description: string;
}

export interface UpdateSkillRequest {
  name?: string;
  slug?: string;
  description?: string;
  version?: string;
  is_public?: boolean;
  tags?: string[];
  platform_support?: string[];
}

export interface SkillFile {
  path: string;
  content: string;
}

export interface SkillMetadata {
  name: string;
  description: string;
  version: string;
  tags: string[];
  platform_support: string[];
  author: string;
  created_at: string;
  updated_at: string;
}

export interface Version {
  id: string;
  skill_id: string;
  tree_id: string;
  message: string;
  version_number: number;
  created_at: string;
}

export interface VersionDiff {
  added: string[];
  removed: string[];
  modified: string[];
}
