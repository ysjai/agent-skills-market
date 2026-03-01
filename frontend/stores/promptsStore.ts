import { create } from 'zustand';
import type { PromptsState } from './types';
import type { Prompt } from '@/types/prompt';

export const usePromptsStore = create<PromptsState>((set, get) => ({
  prompts: [],
  selectedPrompt: null,
  isLoading: true,
  errorMessage: null,
  searchQuery: '',
  selectedTag: null,

  setPrompts: (prompts: Prompt[]) => set({ prompts, isLoading: false }),

  addPrompt: (prompt: Prompt) =>
    set((state) => ({
      prompts: [prompt, ...state.prompts],
    })),

  removePrompt: (id: string) =>
    set((state) => ({
      prompts: state.prompts.filter((prompt) => prompt.id !== id),
    })),

  updatePrompt: (id: string, updates: Partial<Prompt>) =>
    set((state) => ({
      prompts: state.prompts.map((prompt) =>
        prompt.id === id ? { ...prompt, ...updates } : prompt
      ),
    })),

  setSelectedPrompt: (prompt: Prompt | null) => set({ selectedPrompt: prompt }),

  setIsLoading: (isLoading: boolean) => set({ isLoading }),

  setErrorMessage: (errorMessage: string | null) =>
    set({ errorMessage, isLoading: false }),

  setSearchQuery: (query: string) => set({ searchQuery: query }),

  setSelectedTag: (tag: string | null) => set({ selectedTag: tag }),

  getFilteredPrompts: () => {
    const { prompts, searchQuery, selectedTag } = get();
    let filtered = prompts;

    // Filter by search query (title or description)
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (prompt) =>
          prompt.title.toLowerCase().includes(query) ||
          prompt.description?.toLowerCase().includes(query)
      );
    }

    // Filter by selected tag
    if (selectedTag) {
      filtered = filtered.filter((prompt) => prompt.tags.includes(selectedTag));
    }

    return filtered;
  },
}));
