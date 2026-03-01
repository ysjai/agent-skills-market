'use client';

import React, { useState, KeyboardEvent, ChangeEvent, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Input } from '@/components/ui/Input';

export interface TagInputProps {
  tags: string[];
  onChange: (tags: string[]) => void;
  className?: string;
}

export function TagInput({ tags, onChange, className }: TagInputProps) {
  const t = useTranslations('prompts');
  const [inputValue, setInputValue] = useState('');

  const handleAddTag = useCallback((value: string) => {
    const newTag = value.trim().toLowerCase();
    
    // Validation
    if (!newTag) return;
    if (newTag.length > 50) return;
    if (tags.length >= 20) return;
    if (tags.includes(newTag)) return;
    
    onChange([...tags, newTag]);
    setInputValue('');
  }, [tags, onChange]);

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      handleAddTag(inputValue);
    } else if (e.key === 'Backspace' && inputValue === '' && tags.length > 0) {
      e.preventDefault();
      const newTags = [...tags];
      newTags.pop();
      onChange(newTags);
    }
  };

  const handleBlur = () => {
    if (inputValue.trim()) {
      handleAddTag(inputValue);
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleRemoveTag = (tagToRemove: string) => {
    onChange(tags.filter((tag) => tag !== tagToRemove));
  };

  return (
    <div className={cn("flex flex-col gap-2", className)}>
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center gap-1 rounded-md bg-gray-100 px-2 py-1 text-sm text-gray-700"
          >
            {tag}
            <button
              type="button"
              onClick={() => handleRemoveTag(tag)}
              className="text-gray-400 hover:text-gray-600 focus:outline-none"
              aria-label={`Remove ${tag} tag`}
            >
              <X className="h-3 w-3" />
            </button>
          </span>
        ))}
      </div>
      <div className="relative">
        <Input
          type="text"
          value={inputValue}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onBlur={handleBlur}
          placeholder={tags.length < 20 ? t('addTag') : ''}
          disabled={tags.length >= 20}
          className="w-full"
        />
      </div>
    </div>
  );
}
