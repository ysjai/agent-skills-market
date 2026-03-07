import { beforeEach, describe, expect, it } from 'bun:test';
import { useFavoritesStore } from '../favoritesStore';
import type { SkillFavorite } from '@/types/market';

const resetStore = () => {
  useFavoritesStore.setState({
    favorites: [],
    total: 0,
    isLoading: false,
    error: null,
  });
};

const mockFavorite = (id: string, name: string): SkillFavorite => ({
  id,
  user_id: 'user-1',
  shared_skill_id: `shared-${id}`,
  snapshot_name: name,
  snapshot_description: `${name} description`,
  snapshot_slug: name.toLowerCase().replace(/\s+/g, '-'),
  snapshot_author_name: 'tester',
  snapshot_status: 'active',
  created_at: '2024-01-01T00:00:00Z',
});

describe('favoritesStore', () => {
  beforeEach(() => {
    resetStore();
  });

  it('should have correct initial state', () => {
    const state = useFavoritesStore.getState();

    expect(state.favorites).toEqual([]);
    expect(state.total).toBe(0);
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('should update favorites and total', () => {
    const favorites = [mockFavorite('1', 'Favorite One'), mockFavorite('2', 'Favorite Two')];
    const { setFavorites, setTotal } = useFavoritesStore.getState();

    setFavorites(favorites);
    setTotal(favorites.length);

    const state = useFavoritesStore.getState();
    expect(state.favorites).toEqual(favorites);
    expect(state.total).toBe(2);
  });

  it('should add favorite and increment total', () => {
    const existingFavorite = mockFavorite('1', 'Existing Favorite');
    const newFavorite = mockFavorite('2', 'New Favorite');

    useFavoritesStore.getState().setFavorites([existingFavorite]);
    useFavoritesStore.getState().setTotal(1);
    useFavoritesStore.getState().addFavorite(newFavorite);

    const state = useFavoritesStore.getState();
    expect(state.favorites).toEqual([newFavorite, existingFavorite]);
    expect(state.total).toBe(2);
  });

  it('should remove favorite by id and decrement total', () => {
    const favoriteOne = mockFavorite('1', 'Favorite One');
    const favoriteTwo = mockFavorite('2', 'Favorite Two');

    useFavoritesStore.getState().setFavorites([favoriteOne, favoriteTwo]);
    useFavoritesStore.getState().setTotal(2);
    useFavoritesStore.getState().removeFavorite(favoriteOne.id);

    const state = useFavoritesStore.getState();
    expect(state.favorites).toEqual([favoriteTwo]);
    expect(state.total).toBe(1);
  });
});
