import { usePromptsStore } from '@/stores/promptsStore';
import type { Prompt } from '@/types/prompt';

// Sample mock data
const mockPrompt1: Prompt = {
  id: '123e4567-e89b-12d3-a456-426614174000',
  user_id: 'user-uuid-1',
  title: 'Test Prompt',
  content: 'Hello {{name}}',
  description: 'A test description',
  tags: ['test', 'greeting'],
  version: 1,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

const mockPrompt2: Prompt = {
  id: '223e4567-e89b-12d3-a456-426614174001',
  user_id: 'user-uuid-1',
  title: 'Another Prompt',
  content: 'Goodbye {{name}}',
  description: 'Farewell message template',
  tags: ['farewell', 'template'],
  version: 2,
  created_at: '2024-01-02T00:00:00Z',
  updated_at: '2024-01-02T00:00:00Z',
};

const mockPrompt3: Prompt = {
  id: '323e4567-e89b-12d3-a456-426614174002',
  user_id: 'user-uuid-1',
  title: 'Code Review Helper',
  content: 'Please review this code: {{code}}',
  description: 'Helps with code review tasks',
  tags: ['test', 'code', 'review'],
  version: 1,
  created_at: '2024-01-03T00:00:00Z',
  updated_at: '2024-01-03T00:00:00Z',
};

// Reset store before each test
beforeEach(() => {
  usePromptsStore.setState({
    prompts: [],
    selectedPrompt: null,
    isLoading: true,
    errorMessage: null,
    searchQuery: '',
    selectedTag: null,
  });
});

describe('usePromptsStore', () => {
  describe('initial state', () => {
    test('has empty prompts array', () => {
      const { prompts } = usePromptsStore.getState();
      expect(prompts).toEqual([]);
    });

    test('has null selectedPrompt', () => {
      const { selectedPrompt } = usePromptsStore.getState();
      expect(selectedPrompt).toBeNull();
    });

    test('has isLoading true', () => {
      const { isLoading } = usePromptsStore.getState();
      expect(isLoading).toBe(true);
    });

    test('has null errorMessage', () => {
      const { errorMessage } = usePromptsStore.getState();
      expect(errorMessage).toBeNull();
    });

    test('has empty searchQuery', () => {
      const { searchQuery } = usePromptsStore.getState();
      expect(searchQuery).toBe('');
    });

    test('has null selectedTag', () => {
      const { selectedTag } = usePromptsStore.getState();
      expect(selectedTag).toBeNull();
    });
  });

  describe('setPrompts', () => {
    test('sets prompts and sets isLoading to false', () => {
      const { setPrompts } = usePromptsStore.getState();
      setPrompts([mockPrompt1, mockPrompt2]);

      const { prompts, isLoading } = usePromptsStore.getState();
      expect(prompts).toEqual([mockPrompt1, mockPrompt2]);
      expect(isLoading).toBe(false);
    });

    test('replaces existing prompts', () => {
      const { setPrompts } = usePromptsStore.getState();
      setPrompts([mockPrompt1]);
      setPrompts([mockPrompt2, mockPrompt3]);

      const { prompts } = usePromptsStore.getState();
      expect(prompts).toHaveLength(2);
      expect(prompts[0]).toEqual(mockPrompt2);
    });

    test('sets empty array', () => {
      const { setPrompts } = usePromptsStore.getState();
      setPrompts([mockPrompt1]);
      setPrompts([]);

      const { prompts } = usePromptsStore.getState();
      expect(prompts).toEqual([]);
    });
  });

  describe('addPrompt', () => {
    test('prepends prompt to the beginning', () => {
      const { setPrompts, addPrompt } = usePromptsStore.getState();
      setPrompts([mockPrompt2]);
      addPrompt(mockPrompt1);

      const { prompts } = usePromptsStore.getState();
      expect(prompts).toHaveLength(2);
      expect(prompts[0]).toEqual(mockPrompt1);
      expect(prompts[1]).toEqual(mockPrompt2);
    });

    test('adds to empty store', () => {
      const { addPrompt } = usePromptsStore.getState();
      addPrompt(mockPrompt1);

      const { prompts } = usePromptsStore.getState();
      expect(prompts).toHaveLength(1);
      expect(prompts[0]).toEqual(mockPrompt1);
    });

    test('multiple addPrompt calls prepend in order', () => {
      const { addPrompt } = usePromptsStore.getState();
      addPrompt(mockPrompt1);
      addPrompt(mockPrompt2);

      const { prompts } = usePromptsStore.getState();
      expect(prompts[0]).toEqual(mockPrompt2);
      expect(prompts[1]).toEqual(mockPrompt1);
    });
  });

  describe('removePrompt', () => {
    test('removes prompt by id', () => {
      const { setPrompts, removePrompt } = usePromptsStore.getState();
      setPrompts([mockPrompt1, mockPrompt2, mockPrompt3]);
      removePrompt(mockPrompt2.id);

      const { prompts } = usePromptsStore.getState();
      expect(prompts).toHaveLength(2);
      expect(prompts.find((p) => p.id === mockPrompt2.id)).toBeUndefined();
    });

    test('does nothing if id not found', () => {
      const { setPrompts, removePrompt } = usePromptsStore.getState();
      setPrompts([mockPrompt1, mockPrompt2]);
      removePrompt('nonexistent-id');

      const { prompts } = usePromptsStore.getState();
      expect(prompts).toHaveLength(2);
    });

    test('removes from single-item store', () => {
      const { setPrompts, removePrompt } = usePromptsStore.getState();
      setPrompts([mockPrompt1]);
      removePrompt(mockPrompt1.id);

      const { prompts } = usePromptsStore.getState();
      expect(prompts).toHaveLength(0);
    });
  });

  describe('updatePrompt', () => {
    test('updates prompt fields by id', () => {
      const { setPrompts, updatePrompt } = usePromptsStore.getState();
      setPrompts([mockPrompt1, mockPrompt2]);
      updatePrompt(mockPrompt1.id, { title: 'Updated Title', version: 2 });

      const { prompts } = usePromptsStore.getState();
      const updated = prompts.find((p) => p.id === mockPrompt1.id);
      expect(updated?.title).toBe('Updated Title');
      expect(updated?.version).toBe(2);
      expect(updated?.content).toBe(mockPrompt1.content); // unchanged fields preserved
    });

    test('does not affect other prompts', () => {
      const { setPrompts, updatePrompt } = usePromptsStore.getState();
      setPrompts([mockPrompt1, mockPrompt2]);
      updatePrompt(mockPrompt1.id, { title: 'Changed' });

      const { prompts } = usePromptsStore.getState();
      const other = prompts.find((p) => p.id === mockPrompt2.id);
      expect(other).toEqual(mockPrompt2);
    });

    test('does nothing if id not found', () => {
      const { setPrompts, updatePrompt } = usePromptsStore.getState();
      setPrompts([mockPrompt1]);
      updatePrompt('nonexistent-id', { title: 'Should not change' });

      const { prompts } = usePromptsStore.getState();
      expect(prompts[0]).toEqual(mockPrompt1);
    });
  });

  describe('setSelectedPrompt', () => {
    test('sets selectedPrompt', () => {
      const { setSelectedPrompt } = usePromptsStore.getState();
      setSelectedPrompt(mockPrompt1);

      const { selectedPrompt } = usePromptsStore.getState();
      expect(selectedPrompt).toEqual(mockPrompt1);
    });

    test('sets selectedPrompt to null', () => {
      const { setSelectedPrompt } = usePromptsStore.getState();
      setSelectedPrompt(mockPrompt1);
      setSelectedPrompt(null);

      const { selectedPrompt } = usePromptsStore.getState();
      expect(selectedPrompt).toBeNull();
    });
  });

  describe('setSearchQuery', () => {
    test('sets searchQuery', () => {
      const { setSearchQuery } = usePromptsStore.getState();
      setSearchQuery('hello');

      const { searchQuery } = usePromptsStore.getState();
      expect(searchQuery).toBe('hello');
    });

    test('sets searchQuery to empty string', () => {
      const { setSearchQuery } = usePromptsStore.getState();
      setSearchQuery('something');
      setSearchQuery('');

      const { searchQuery } = usePromptsStore.getState();
      expect(searchQuery).toBe('');
    });
  });

  describe('setSelectedTag', () => {
    test('sets selectedTag', () => {
      const { setSelectedTag } = usePromptsStore.getState();
      setSelectedTag('test');

      const { selectedTag } = usePromptsStore.getState();
      expect(selectedTag).toBe('test');
    });

    test('sets selectedTag to null', () => {
      const { setSelectedTag } = usePromptsStore.getState();
      setSelectedTag('test');
      setSelectedTag(null);

      const { selectedTag } = usePromptsStore.getState();
      expect(selectedTag).toBeNull();
    });
  });

  describe('getFilteredPrompts', () => {
    beforeEach(() => {
      usePromptsStore.getState().setPrompts([mockPrompt1, mockPrompt2, mockPrompt3]);
    });

    test('returns all prompts when no filters set', () => {
      const { getFilteredPrompts } = usePromptsStore.getState();
      const result = getFilteredPrompts();
      expect(result).toHaveLength(3);
    });

    test('filters by title match (case insensitive)', () => {
      const { setSearchQuery, getFilteredPrompts } = usePromptsStore.getState();
      setSearchQuery('test');

      const result = getFilteredPrompts();
      // mockPrompt1 has title 'Test Prompt', mockPrompt3 has title 'Code Review Helper' but tags 'test'
      // Only title+description matching — mockPrompt1 matches title, mockPrompt3 does NOT match title/description by 'test'
      expect(result.some((p) => p.id === mockPrompt1.id)).toBe(true);
    });

    test('filters by description match (case insensitive)', () => {
      const { setSearchQuery, getFilteredPrompts } = usePromptsStore.getState();
      setSearchQuery('farewell');

      const result = getFilteredPrompts();
      expect(result).toHaveLength(1);
      expect(result[0].id).toBe(mockPrompt2.id);
    });

    test('filters by title partial match', () => {
      const { setSearchQuery, getFilteredPrompts } = usePromptsStore.getState();
      setSearchQuery('code review');

      const result = getFilteredPrompts();
      expect(result).toHaveLength(1);
      expect(result[0].id).toBe(mockPrompt3.id);
    });

    test('returns empty array when no title/description matches', () => {
      const { setSearchQuery, getFilteredPrompts } = usePromptsStore.getState();
      setSearchQuery('zzznomatch');

      const result = getFilteredPrompts();
      expect(result).toHaveLength(0);
    });

    test('filters by selectedTag', () => {
      const { setSelectedTag, getFilteredPrompts } = usePromptsStore.getState();
      setSelectedTag('test');

      const result = getFilteredPrompts();
      // mockPrompt1 tags: ['test', 'greeting'], mockPrompt3 tags: ['test', 'code', 'review']
      expect(result).toHaveLength(2);
      expect(result.some((p) => p.id === mockPrompt1.id)).toBe(true);
      expect(result.some((p) => p.id === mockPrompt3.id)).toBe(true);
    });

    test('filters by selectedTag returns only matching prompts', () => {
      const { setSelectedTag, getFilteredPrompts } = usePromptsStore.getState();
      setSelectedTag('farewell');

      const result = getFilteredPrompts();
      expect(result).toHaveLength(1);
      expect(result[0].id).toBe(mockPrompt2.id);
    });

    test('filters by both searchQuery and selectedTag (intersection)', () => {
      const { setSearchQuery, setSelectedTag, getFilteredPrompts } = usePromptsStore.getState();
      setSearchQuery('test');
      setSelectedTag('greeting');

      const result = getFilteredPrompts();
      // mockPrompt1: title 'Test Prompt' matches 'test' AND has 'greeting' tag
      expect(result).toHaveLength(1);
      expect(result[0].id).toBe(mockPrompt1.id);
    });

    test('returns empty when searchQuery and selectedTag have no intersection', () => {
      const { setSearchQuery, setSelectedTag, getFilteredPrompts } = usePromptsStore.getState();
      setSearchQuery('farewell');
      setSelectedTag('test');

      const result = getFilteredPrompts();
      // mockPrompt2 matches description 'farewell' but doesn't have 'test' tag
      expect(result).toHaveLength(0);
    });

    test('returns all when filters are cleared', () => {
      const { setSearchQuery, setSelectedTag, getFilteredPrompts } = usePromptsStore.getState();
      setSearchQuery('test');
      setSelectedTag('greeting');
      setSearchQuery('');
      setSelectedTag(null);

      const result = getFilteredPrompts();
      expect(result).toHaveLength(3);
    });

    test('description match works with null description (does not throw)', () => {
      const promptWithNullDesc: Prompt = {
        ...mockPrompt1,
        id: 'null-desc-id',
        description: null,
        title: 'Prompt Without Desc',
      };
      usePromptsStore.getState().setPrompts([promptWithNullDesc]);
      usePromptsStore.getState().setSearchQuery('description');

      const result = usePromptsStore.getState().getFilteredPrompts();
      expect(result).toHaveLength(0);
    });
  });
});
