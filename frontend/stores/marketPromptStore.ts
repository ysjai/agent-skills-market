import { create } from 'zustand';
import type { SharedPrompt, PromptMarketSearchParams } from '@/types/prompt-market';
import { api } from '@/lib/api';

interface MarketPromptState {
  prompts: SharedPrompt[];
  total: number;
  isLoading: boolean;
  error: string | null;
  filters: PromptMarketSearchParams;
  setPrompts: (prompts: SharedPrompt[]) => void;
  setTotal: (total: number) => void;
  setIsLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  setFilters: (filters: Partial<PromptMarketSearchParams>) => void;
  resetFilters: () => void;
  loadMarketPrompts: (params?: Partial<PromptMarketSearchParams>) => Promise<void>;
  toggleLikeOptimistic: (promptId: string) => void;
  toggleFavoriteOptimistic: (promptId: string) => void;
}

const defaultFilters: PromptMarketSearchParams = {
  keyword: '',
  tags: [],
  sort_by: 'newest',
  skip: 0,
  limit: 20,
};

export const useMarketPromptStore = create<MarketPromptState>((set, get) => ({
  prompts: [],
  total: 0,
  isLoading: false,
  error: null,
  filters: defaultFilters,

  setPrompts: (prompts) => set({ prompts }),
  setTotal: (total) => set({ total }),
  setIsLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  setFilters: (newFilters) =>
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    })),
  resetFilters: () => set({ filters: defaultFilters }),

  loadMarketPrompts: async (params) => {
    set((state) => ({
      isLoading: true,
      error: null,
      filters: params ? { ...state.filters, ...params } : state.filters,
    }));

    try {
      const data = await api.getMarketPrompts(get().filters);
      set({ prompts: data.items, total: data.total, isLoading: false });
    } catch (err: unknown) {
      set({
        isLoading: false,
        error: err instanceof Error ? err.message : 'Failed to load market prompts',
      });
    }
  },

  toggleLikeOptimistic: (promptId) => {
    set((state) => ({
      prompts: state.prompts.map((prompt) => {
        if (prompt.id !== promptId) return prompt;
        const nextLiked = !prompt.is_liked;
        return {
          ...prompt,
          is_liked: nextLiked,
          like_count: Math.max(0, prompt.like_count + (nextLiked ? 1 : -1)),
        };
      }),
    }));
  },

  toggleFavoriteOptimistic: (promptId) => {
    set((state) => ({
      prompts: state.prompts.map((prompt) => {
        if (prompt.id !== promptId) return prompt;
        const nextFavorited = !prompt.is_favorited;
        return {
          ...prompt,
          is_favorited: nextFavorited,
          favorite_count: Math.max(0, prompt.favorite_count + (nextFavorited ? 1 : -1)),
        };
      }),
    }));
  },
}));
