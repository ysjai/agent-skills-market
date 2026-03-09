export interface Category {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  display_order: number;
  is_active: boolean;
}

export interface CategoryListResponse {
  items: Category[];
  total: number;
}

export interface SharedSkill {
  id: string;
  skill_id: string | null;
  user_id: string;
  category_id: string;
  category?: Category;
  share_message: string | null;
  like_count: number;
  favorite_count: number;
  status: "active" | "withdrawn";
  name: string;
  description: string | null;
  author_name: string;
  created_at: string;
  updated_at: string;
  // For market listing responses with auth
  is_liked?: boolean;
  is_favorited?: boolean;
}

export interface SharedSkillListResponse {
  items: SharedSkill[];
  total: number;
}

export interface ShareSkillRequest {
  category_id: string;
  share_message?: string;
}

export interface SkillFavorite {
  id: string;
  user_id: string;
  shared_skill_id: string;
  snapshot_name: string;
  snapshot_description: string | null;
  snapshot_slug: string;
  snapshot_author_name: string;
  snapshot_status: "active" | "skill_withdrawn" | "skill_deleted";
  created_at: string;
  like_count: number;
  is_liked: boolean;
}

export interface FavoriteListResponse {
  items: SkillFavorite[];
  total: number;
}

export interface MarketSearchParams {
  keyword?: string;
  category_id?: string;
  sort_by?: "newest" | "popular";
  skip?: number;
  limit?: number;
}
