import type { Skill } from '@/types/skill';
import type { Prompt } from '@/types/prompt';
import type { User } from '@/types/user';


// Auth Store
export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setAuthenticated: (value: boolean) => void;
  logout: () => void;
}

// Skills Store
export interface SkillsState {
  skills: Skill[];
  isLoading: boolean;
  errorMessage: string | null;
  searchQuery: string;
  setSkills: (skills: Skill[]) => void;
  addSkill: (skill: Skill) => void;
  removeSkill: (id: string) => void;
  updateSkill: (id: string, updates: Partial<Skill>) => void;
  setIsLoading: (isLoading: boolean) => void;
  setErrorMessage: (errorMessage: string | null) => void;
  setSearchQuery: (query: string) => void;
  getFilteredSkills: () => Skill[];
}

// Prompts Store
export interface PromptsState {
  prompts: Prompt[];
  selectedPrompt: Prompt | null;
  isLoading: boolean;
  errorMessage: string | null;
  searchQuery: string;
  selectedTag: string | null;
  setPrompts: (prompts: Prompt[]) => void;
  addPrompt: (prompt: Prompt) => void;
  removePrompt: (id: string) => void;
  updatePrompt: (id: string, updates: Partial<Prompt>) => void;
  setSelectedPrompt: (prompt: Prompt | null) => void;
  setIsLoading: (isLoading: boolean) => void;
  setErrorMessage: (errorMessage: string | null) => void;
  setSearchQuery: (query: string) => void;
  setSelectedTag: (tag: string | null) => void;
  getFilteredPrompts: () => Prompt[];
}

// UI Store (for dialog states, etc.)
export interface UIState {
  isCreateDialogOpen: boolean;
  isImportDialogOpen: boolean;
  isUserMenuOpen: boolean;
  setCreateDialogOpen: (open: boolean) => void;
  setImportDialogOpen: (open: boolean) => void;
  setUserMenuOpen: (open: boolean) => void;
}
