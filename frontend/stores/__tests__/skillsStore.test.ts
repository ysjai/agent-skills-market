import { describe, it, expect, beforeEach } from 'bun:test';
import { useSkillsStore } from '../skillsStore';
import type { Skill } from '@/types/skill';

// Helper function to get fresh store instance
const getStore = () => useSkillsStore.getState();

// Reset store before each test
const resetStore = () => {
  useSkillsStore.setState({
    skills: [],
    isLoading: true,
    errorMessage: null,
    searchQuery: '',
  });
};

// Mock skills data
const createMockSkill = (id: string, name: string, description?: string): Skill => ({
  id,
  user_id: 'user-1',
  name,
  slug: name.toLowerCase().replace(/\s+/g, '-'),
  description: description || null,
  version: 1,
  is_public: false,
  tree_id: null,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
});

describe('skillsStore', () => {
  beforeEach(() => {
    resetStore();
  });

  describe('Initial State', () => {
    it('should have empty skills array', () => {
      const state = getStore();
      expect(state.skills).toEqual([]);
    });

    it('should have isLoading as true', () => {
      const state = getStore();
      expect(state.isLoading).toBe(true);
    });

    it('should have errorMessage as null', () => {
      const state = getStore();
      expect(state.errorMessage).toBeNull();
    });

    it('should have empty searchQuery', () => {
      const state = getStore();
      expect(state.searchQuery).toBe('');
    });
  });

  describe('setSkills', () => {
    it('should set skills array', () => {
      const skills: Skill[] = [
        createMockSkill('1', 'Test Skill'),
        createMockSkill('2', 'Another Skill'),
      ];
      
      getStore().setSkills(skills);
      
      expect(getStore().skills).toEqual(skills);
    });

    it('should set isLoading to false', () => {
      const skills: Skill[] = [createMockSkill('1', 'Test Skill')];
      
      getStore().setSkills(skills);
      
      expect(getStore().isLoading).toBe(false);
    });

    it('should replace existing skills', () => {
      const initialSkills: Skill[] = [createMockSkill('1', 'Old Skill')];
      getStore().setSkills(initialSkills);
      
      const newSkills: Skill[] = [createMockSkill('2', 'New Skill')];
      getStore().setSkills(newSkills);
      
      expect(getStore().skills).toEqual(newSkills);
      expect(getStore().skills.length).toBe(1);
    });
  });

  describe('addSkill', () => {
    it('should add skill to the beginning of the list', () => {
      const existingSkill = createMockSkill('1', 'Existing Skill');
      getStore().setSkills([existingSkill]);
      
      const newSkill = createMockSkill('2', 'New Skill');
      getStore().addSkill(newSkill);
      
      const skills = getStore().skills;
      expect(skills.length).toBe(2);
      expect(skills[0]).toEqual(newSkill);
      expect(skills[1]).toEqual(existingSkill);
    });

    it('should add skill to empty list', () => {
      const newSkill = createMockSkill('1', 'First Skill');
      getStore().addSkill(newSkill);
      
      expect(getStore().skills).toEqual([newSkill]);
    });

    it('should add multiple skills in correct order', () => {
      const skill1 = createMockSkill('1', 'First Skill');
      const skill2 = createMockSkill('2', 'Second Skill');
      const skill3 = createMockSkill('3', 'Third Skill');
      
      getStore().addSkill(skill1);
      getStore().addSkill(skill2);
      getStore().addSkill(skill3);
      
      const skills = getStore().skills;
      expect(skills.length).toBe(3);
      expect(skills[0]).toEqual(skill3);
      expect(skills[1]).toEqual(skill2);
      expect(skills[2]).toEqual(skill1);
    });
  });

  describe('removeSkill', () => {
    it('should remove skill by id', () => {
      const skill1 = createMockSkill('1', 'Skill 1');
      const skill2 = createMockSkill('2', 'Skill 2');
      const skill3 = createMockSkill('3', 'Skill 3');
      getStore().setSkills([skill1, skill2, skill3]);
      
      getStore().removeSkill('2');
      
      const skills = getStore().skills;
      expect(skills.length).toBe(2);
      expect(skills.find(s => s.id === '2')).toBeUndefined();
      expect(skills.find(s => s.id === '1')).toBeDefined();
      expect(skills.find(s => s.id === '3')).toBeDefined();
    });

    it('should not modify list if id does not exist', () => {
      const skill1 = createMockSkill('1', 'Skill 1');
      const skill2 = createMockSkill('2', 'Skill 2');
      getStore().setSkills([skill1, skill2]);
      
      getStore().removeSkill('999');
      
      expect(getStore().skills.length).toBe(2);
      expect(getStore().skills).toEqual([skill1, skill2]);
    });

    it('should handle empty skills array', () => {
      getStore().removeSkill('1');
      
      expect(getStore().skills).toEqual([]);
    });

    it('should remove only the matching skill when multiple have similar ids', () => {
      const skill1 = createMockSkill('10', 'Skill 10');
      const skill2 = createMockSkill('1', 'Skill 1');
      getStore().setSkills([skill1, skill2]);
      
      getStore().removeSkill('1');
      
      const skills = getStore().skills;
      expect(skills.length).toBe(1);
      expect(skills[0].id).toBe('10');
    });
  });

  describe('updateSkill', () => {
    it('should update skill fields by id', () => {
      const skill = createMockSkill('1', 'Original Name', 'Original Description');
      getStore().setSkills([skill]);
      
      getStore().updateSkill('1', { name: 'Updated Name', description: 'Updated Description' });
      
      const updatedSkill = getStore().skills[0];
      expect(updatedSkill.name).toBe('Updated Name');
      expect(updatedSkill.description).toBe('Updated Description');
      expect(updatedSkill.id).toBe('1'); // unchanged
      expect(updatedSkill.slug).toBe('original-name'); // unchanged
    });

    it('should update only specified fields', () => {
      const skill = createMockSkill('1', 'Original Name', 'Original Description');
      getStore().setSkills([skill]);
      
      getStore().updateSkill('1', { name: 'Updated Name' });
      
      const updatedSkill = getStore().skills[0];
      expect(updatedSkill.name).toBe('Updated Name');
      expect(updatedSkill.description).toBe('Original Description');
    });

    it('should not modify list if id does not exist', () => {
      const skill = createMockSkill('1', 'Skill 1');
      getStore().setSkills([skill]);
      
      getStore().updateSkill('999', { name: 'Updated Name' });
      
      expect(getStore().skills[0].name).toBe('Skill 1');
    });

    it('should update only the matching skill when multiple exist', () => {
      const skill1 = createMockSkill('1', 'Skill 1');
      const skill2 = createMockSkill('2', 'Skill 2');
      getStore().setSkills([skill1, skill2]);
      
      getStore().updateSkill('2', { name: 'Updated Skill 2' });
      
      const skills = getStore().skills;
      expect(skills[0].name).toBe('Skill 1');
      expect(skills[1].name).toBe('Updated Skill 2');
    });

    it('should handle partial updates with various field types', () => {
      const skill = createMockSkill('1', 'Skill 1');
      getStore().setSkills([skill]);
      
      getStore().updateSkill('1', { 
        name: 'New Name',
        is_public: true,
        version: 2
      });
      
      const updatedSkill = getStore().skills[0];
      expect(updatedSkill.name).toBe('New Name');
      expect(updatedSkill.is_public).toBe(true);
      expect(updatedSkill.version).toBe(2);
    });
  });

  describe('setIsLoading', () => {
    it('should set isLoading to true', () => {
      getStore().setIsLoading(true);
      
      expect(getStore().isLoading).toBe(true);
    });

    it('should set isLoading to false', () => {
      getStore().setIsLoading(true); // First set to true
      getStore().setIsLoading(false);
      
      expect(getStore().isLoading).toBe(false);
    });

    it('should not affect other state', () => {
      const skills = [createMockSkill('1', 'Skill 1')];
      getStore().setSkills(skills);
      getStore().setSearchQuery('test query');
      
      getStore().setIsLoading(true);
      
      expect(getStore().skills).toEqual(skills);
      expect(getStore().searchQuery).toBe('test query');
    });
  });

  describe('setErrorMessage', () => {
    it('should set error message', () => {
      getStore().setErrorMessage('Something went wrong');
      
      expect(getStore().errorMessage).toBe('Something went wrong');
    });

    it('should set errorMessage to null', () => {
      getStore().setErrorMessage('Error message');
      getStore().setErrorMessage(null);
      
      expect(getStore().errorMessage).toBeNull();
    });

    it('should set isLoading to false', () => {
      getStore().setIsLoading(true);
      getStore().setErrorMessage('Error');
      
      expect(getStore().isLoading).toBe(false);
    });

    it('should handle empty string error', () => {
      getStore().setErrorMessage('');
      
      expect(getStore().errorMessage).toBe('');
      expect(getStore().isLoading).toBe(false);
    });
  });

  describe('setSearchQuery', () => {
    it('should set search query', () => {
      getStore().setSearchQuery('test query');
      
      expect(getStore().searchQuery).toBe('test query');
    });

    it('should set empty string', () => {
      getStore().setSearchQuery('test');
      getStore().setSearchQuery('');
      
      expect(getStore().searchQuery).toBe('');
    });

    it('should handle query with special characters', () => {
      getStore().setSearchQuery('test-query_123!@#');
      
      expect(getStore().searchQuery).toBe('test-query_123!@#');
    });

    it('should handle query with spaces', () => {
      getStore().setSearchQuery('hello world test');
      
      expect(getStore().searchQuery).toBe('hello world test');
    });
  });

  describe('getFilteredSkills', () => {
    it('should return all skills when searchQuery is empty', () => {
      const skills = [
        createMockSkill('1', 'React Skill'),
        createMockSkill('2', 'Vue Skill'),
      ];
      getStore().setSkills(skills);
      
      const filtered = getStore().getFilteredSkills();
      
      expect(filtered).toEqual(skills);
    });

    it('should filter by name (case insensitive)', () => {
      const skills = [
        createMockSkill('1', 'React Skill'),
        createMockSkill('2', 'Vue Skill'),
        createMockSkill('3', 'Angular Skill'),
      ];
      getStore().setSkills(skills);
      getStore().setSearchQuery('react');
      
      const filtered = getStore().getFilteredSkills();
      
      expect(filtered.length).toBe(1);
      expect(filtered[0].name).toBe('React Skill');
    });

    it('should filter by name (uppercase query)', () => {
      const skills = [
        createMockSkill('1', 'React Skill'),
        createMockSkill('2', 'Vue Skill'),
      ];
      getStore().setSkills(skills);
      getStore().setSearchQuery('REACT');
      
      const filtered = getStore().getFilteredSkills();
      
      expect(filtered.length).toBe(1);
      expect(filtered[0].name).toBe('React Skill');
    });

    it('should filter by description (case insensitive)', () => {
      const skills = [
        createMockSkill('1', 'Skill 1', 'A frontend framework'),
        createMockSkill('2', 'Skill 2', 'A backend framework'),
        createMockSkill('3', 'Skill 3', 'A database tool'),
      ];
      getStore().setSkills(skills);
      getStore().setSearchQuery('frontend');
      
      const filtered = getStore().getFilteredSkills();
      
      expect(filtered.length).toBe(1);
      expect(filtered[0].id).toBe('1');
    });

    it('should filter by description (uppercase query)', () => {
      const skills = [
        createMockSkill('1', 'Skill 1', 'A frontend framework'),
        createMockSkill('2', 'Skill 2', 'A backend framework'),
      ];
      getStore().setSkills(skills);
      getStore().setSearchQuery('FRONTEND');
      
      const filtered = getStore().getFilteredSkills();
      
      expect(filtered.length).toBe(1);
      expect(filtered[0].id).toBe('1');
    });

    it('should match skills where name OR description contains query', () => {
      const skills = [
        createMockSkill('1', 'React Framework', 'A frontend library'),
        createMockSkill('2', 'Vue.js', 'A frontend framework'),
        createMockSkill('3', 'PostgreSQL', 'A database'),
      ];
      getStore().setSkills(skills);
      getStore().setSearchQuery('framework');
      
      const filtered = getStore().getFilteredSkills();
      
      expect(filtered.length).toBe(2);
      expect(filtered.map(s => s.id)).toContain('1');
      expect(filtered.map(s => s.id)).toContain('2');
    });

    it('should return empty array when no matches found', () => {
      const skills = [
        createMockSkill('1', 'React Skill'),
        createMockSkill('2', 'Vue Skill'),
      ];
      getStore().setSkills(skills);
      getStore().setSearchQuery('angular');
      
      const filtered = getStore().getFilteredSkills();
      
      expect(filtered).toEqual([]);
    });

    it('should handle partial matches', () => {
      const skills = [
        createMockSkill('1', 'JavaScript Framework'),
        createMockSkill('2', 'Java Language'),
        createMockSkill('3', 'Python Script'),
      ];
      getStore().setSkills(skills);
      getStore().setSearchQuery('script');
      
      const filtered = getStore().getFilteredSkills();
      
      expect(filtered.length).toBe(2);
      expect(filtered.map(s => s.id)).toContain('1');
      expect(filtered.map(s => s.id)).toContain('3');
    });

    it('should handle skills with null description', () => {
      const skills = [
        createMockSkill('1', 'React Skill'), // description is null
        createMockSkill('2', 'Vue Skill', 'A framework'),
      ];
      getStore().setSkills(skills);
      getStore().setSearchQuery('react');
      
      const filtered = getStore().getFilteredSkills();
      
      expect(filtered.length).toBe(1);
      expect(filtered[0].id).toBe('1');
    });

    it('should handle skills with null description when searching in description', () => {
      const skills = [
        createMockSkill('1', 'React Skill'), // description is null
        createMockSkill('2', 'Vue Skill', 'A framework'),
      ];
      getStore().setSkills(skills);
      getStore().setSearchQuery('framework');
      
      const filtered = getStore().getFilteredSkills();
      
      expect(filtered.length).toBe(1);
      expect(filtered[0].id).toBe('2');
    });

    it('should handle empty skills array', () => {
      getStore().setSearchQuery('react');
      
      const filtered = getStore().getFilteredSkills();
      
      expect(filtered).toEqual([]);
    });

    it('should handle query with spaces', () => {
      const skills = [
        createMockSkill('1', 'React Hooks Guide'),
        createMockSkill('2', 'Vue Composition API'),
      ];
      getStore().setSkills(skills);
      getStore().setSearchQuery('react hooks');
      
      const filtered = getStore().getFilteredSkills();
      
      expect(filtered.length).toBe(1);
      expect(filtered[0].id).toBe('1');
    });
  });
});
