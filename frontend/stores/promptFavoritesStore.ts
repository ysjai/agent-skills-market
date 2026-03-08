import { create } from 'zustand';
import type { PromptFavorite } from '@/types/prompt-market';

interface PromptFavoritesState {
  favorites: PromptFavorite[];
  total: number;
  isLoading: boolean;
  error: string | null;
  setFavorites: (favorites: PromptFavorite[]) => void;
  setTotal: (total: number) => void;
  setIsLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  addFavorite: (favorite: PromptFavorite) => void;
  removeFavorite: (id: string) => void;
  updateFavorite: (id: string, updated: PromptFavorite) => void;
}

export const usePromptFavoritesStore = create<PromptFavoritesState>((set) => ({
  favorites: [],
  total: 0,
  isLoading: false,
  error: null,

  setFavorites: (favorites) => set({ favorites }),
  setTotal: (total) => set({ total }),
  setIsLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  addFavorite: (favorite) =>
    set((state) => ({
      favorites: [favorite, ...state.favorites],
      total: state.total + 1,
    })),
  removeFavorite: (id) =>
    set((state) => ({
      favorites: state.favorites.filter((f) => f.id !== id),
      total: Math.max(0, state.total - 1),
    })),
  updateFavorite: (id, updated) =>
    set((state) => ({
      favorites: state.favorites.map((f) => (f.id === id ? updated : f)),
    })),
}));
