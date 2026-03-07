import { beforeEach, describe, expect, it } from 'bun:test';
import { useMarketStore } from '../marketStore';
import type { Category, SharedSkill } from '@/types/market';

const defaultFilters = {
  keyword: '',
  category_id: '',
  sort_by: 'newest' as const,
  skip: 0,
  limit: 20,
};

const resetStore = () => {
  useMarketStore.setState({
    skills: [],
    total: 0,
    categories: [],
    isLoading: false,
    error: null,
    filters: { ...defaultFilters },
  });
};

const mockSkill = (id: string, name: string): SharedSkill => ({
  id,
  skill_id: `skill-${id}`,
  user_id: 'user-1',
  category_id: 'category-1',
  share_message: `share-${id}`,
  like_count: 0,
  favorite_count: 0,
  status: 'active',
  snapshot_name: name,
  snapshot_description: `${name} description`,
  snapshot_author_name: 'tester',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
});

const mockCategories: Category[] = [
  {
    id: 'category-1',
    name: 'Coding',
    slug: 'coding',
    description: 'Coding skills',
    display_order: 1,
    is_active: true,
  },
  {
    id: 'category-2',
    name: 'Testing',
    slug: 'testing',
    description: 'Testing skills',
    display_order: 2,
    is_active: true,
  },
];

describe('marketStore', () => {
  beforeEach(() => {
    resetStore();
  });

  it('should have correct initial state', () => {
    const state = useMarketStore.getState();

    expect(state.skills).toEqual([]);
    expect(state.total).toBe(0);
    expect(state.categories).toEqual([]);
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
    expect(state.filters).toEqual(defaultFilters);
  });

  it('should update skills and total', () => {
    const skills = [mockSkill('1', 'Skill One'), mockSkill('2', 'Skill Two')];
    const { setSkills, setTotal } = useMarketStore.getState();

    setSkills(skills);
    setTotal(skills.length);

    const state = useMarketStore.getState();
    expect(state.skills).toEqual(skills);
    expect(state.total).toBe(2);
  });

  it('should update loading state', () => {
    const { setIsLoading } = useMarketStore.getState();

    setIsLoading(true);
    expect(useMarketStore.getState().isLoading).toBe(true);

    setIsLoading(false);
    expect(useMarketStore.getState().isLoading).toBe(false);
  });

  it('should update categories', () => {
    useMarketStore.getState().setCategories(mockCategories);

    expect(useMarketStore.getState().categories).toEqual(mockCategories);
  });

  it('should merge filters and keep other fields unchanged', () => {
    const { setFilters } = useMarketStore.getState();

    setFilters({ keyword: 'react', sort_by: 'popular' });

    const state = useMarketStore.getState();
    expect(state.filters).toEqual({
      ...defaultFilters,
      keyword: 'react',
      sort_by: 'popular',
    });
    expect(state.filters.category_id).toBe('');
    expect(state.filters.skip).toBe(0);
    expect(state.filters.limit).toBe(20);
  });
});
