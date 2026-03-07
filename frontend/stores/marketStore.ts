import { create } from 'zustand';
import type { MarketState } from './types';
import type { SharedSkill, Category, MarketSearchParams } from '@/types/market';
import { api } from '@/lib/api';

const defaultFilters: MarketSearchParams = {
  keyword: '',
  category_id: '',
  sort_by: 'newest',
  skip: 0,
  limit: 20,
};

export const useMarketStore = create<MarketState>((set, get) => ({
  skills: [],
  total: 0,
  categories: [],
  isLoading: false,
  error: null,
  filters: defaultFilters,

  setSkills: (skills: SharedSkill[]) => set({ skills }),
  
  setTotal: (total: number) => set({ total }),
  
  setCategories: (categories: Category[]) => set({ categories }),
  
  setIsLoading: (isLoading: boolean) => set({ isLoading }),
  
  setError: (error: string | null) => set({ error }),
  
  setFilters: (newFilters: Partial<MarketSearchParams>) =>
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    })),
    
  resetFilters: () => set({ filters: defaultFilters }),

  loadMarketSkills: async (params) => {
    set((state) => ({
      isLoading: true,
      error: null,
      filters: params ? { ...state.filters, ...params } : state.filters,
    }));

    try {
      const data = await api.getMarketSkills(get().filters);
      set({ skills: data.items, total: data.total, isLoading: false });
    } catch (err: unknown) {
      set({
        isLoading: false,
        error: err instanceof Error ? err.message : 'Failed to load market skills',
      });
    }
  },

  loadCategories: async () => {
    try {
      const response = await api.getCategories();
      set({ categories: response.items });
    } catch {}
  },

  toggleLikeOptimistic: (skillId: string) => {
    set((state) => ({
      skills: state.skills.map((skill) => {
        if (skill.id !== skillId) return skill;
        const nextLiked = !skill.is_liked;
        return {
          ...skill,
          is_liked: nextLiked,
          like_count: Math.max(0, skill.like_count + (nextLiked ? 1 : -1)),
        };
      }),
    }));
  },

  toggleFavoriteOptimistic: (skillId: string) => {
    set((state) => ({
      skills: state.skills.map((skill) => {
        if (skill.id !== skillId) return skill;
        const nextFavorited = !skill.is_favorited;
        return {
          ...skill,
          is_favorited: nextFavorited,
          favorite_count: Math.max(0, skill.favorite_count + (nextFavorited ? 1 : -1)),
        };
      }),
    }));
  },
}));
