export interface SharedPrompt {
  id: string;
  prompt_id: string | null;
  user_id: string;
  title: string;
  description: string | null;
  content: string;
  tags: string[];
  author_name: string;
  share_message: string | null;
  like_count: number;
  favorite_count: number;
  status: string;
  created_at: string;
  updated_at: string;
  is_liked?: boolean;
  is_favorited?: boolean;
}

export interface SharedPromptListResponse {
  items: SharedPrompt[];
  total: number;
}

export interface PromptFavorite {
  id: string;
  user_id: string;
  shared_prompt_id: string | null;
  snapshot_title: string;
  snapshot_content: string;
  snapshot_description: string | null;
  snapshot_tags: string[];
  snapshot_author_name: string;
  snapshot_version: number;
  snapshot_status: "active" | "prompt_withdrawn" | "prompt_deleted";
  created_at: string;
  is_stale: boolean;
}

export interface PromptFavoriteListResponse {
  items: PromptFavorite[];
  total: number;
}

export interface PromptMarketSearchParams {
  keyword?: string;
  tags?: string[];
  sort_by?: "newest" | "popular";
  skip?: number;
  limit?: number;
}
