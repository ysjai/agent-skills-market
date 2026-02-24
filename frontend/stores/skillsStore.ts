import { create } from 'zustand';
import type { SkillsState } from './types';
import type { Skill } from '@/types/skill';

export const useSkillsStore = create<SkillsState>((set, get) => ({
  skills: [],
  isLoading: true,
  errorMessage: null,
  searchQuery: '',

  setSkills: (skills: Skill[]) => set({ skills, isLoading: false }),

  addSkill: (skill: Skill) =>
    set((state) => ({
      skills: [skill, ...state.skills],
    })),

  removeSkill: (id: string) =>
    set((state) => ({
      skills: state.skills.filter((skill) => skill.id !== id),
    })),

  updateSkill: (id: string, updates: Partial<Skill>) =>
    set((state) => ({
      skills: state.skills.map((skill) => (skill.id === id ? { ...skill, ...updates } : skill)),
    })),

  setIsLoading: (isLoading: boolean) => set({ isLoading }),

  setErrorMessage: (errorMessage: string | null) => set({ errorMessage, isLoading: false }),

  setSearchQuery: (query: string) => set({ searchQuery: query }),

  getFilteredSkills: () => {
    const { skills, searchQuery } = get();
    if (!searchQuery) return skills;
    const query = searchQuery.toLowerCase();
    return skills.filter(
      (skill) =>
        skill.name.toLowerCase().includes(query) ||
        skill.description?.toLowerCase().includes(query)
    );
  },
}));
