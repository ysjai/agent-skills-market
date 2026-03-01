export interface Prompt {
  id: string;
  user_id: string;
  title: string;
  content: string;
  description: string | null;
  tags: string[];
  version: number;
  created_at: string;
  updated_at: string;
}

export interface PromptVersion {
  id: string;
  prompt_id: string;
  version_number: number;
  title: string;
  content: string;
  description: string | null;
  tags: string[];
  created_at: string;
}

export interface PromptListResponse {
  items: Prompt[];
  total: number;
}

export interface CreatePromptRequest {
  title: string;
  content: string;
  description?: string;
  tags?: string[];
}

export interface UpdatePromptRequest {
  title?: string;
  content?: string;
  description?: string;
  tags?: string[];
}

export interface ImportPromptRequest {
  markdown_content: string;
}

export interface ExportPromptResponse {
  markdown_content: string;
}
