import { create } from 'zustand';
import type { FavoritesState } from './types';
import type { SkillFavorite } from '@/types/market';

export const useFavoritesStore = create<FavoritesState>((set) => ({
  favorites: [],
  total: 0,
  isLoading: false,
  error: null,

  setFavorites: (favorites: SkillFavorite[]) => set({ favorites }),
  
  setTotal: (total: number) => set({ total }),
  
  setIsLoading: (isLoading: boolean) => set({ isLoading }),
  
  setError: (error: string | null) => set({ error }),
  
  addFavorite: (favorite: SkillFavorite) =>
    set((state) => ({
      favorites: [favorite, ...state.favorites],
      total: state.total + 1,
    })),
    
  removeFavorite: (id: string) =>
    set((state) => ({
      favorites: state.favorites.filter((f) => f.id !== id),
      total: Math.max(0, state.total - 1),
    })),
}));
