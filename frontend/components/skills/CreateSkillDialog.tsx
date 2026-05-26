'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';

import { useRouter } from '@/i18n/routing';
import { Dialog } from '@/components/ui/Dialog';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { api } from '@/lib/api';
import { parseApiError } from '@/lib/errors';
import type { Skill, CreateSkillRequest } from '@/types/skill';

interface CreateSkillDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: (skill: Skill) => void;
}

export function CreateSkillDialog({ open, onClose, onSuccess }: CreateSkillDialogProps) {
  const router = useRouter();
  const t = useTranslations('skills');
  const tForm = useTranslations('skillForm');
  const tCommon = useTranslations('common');

  const [form, setForm] = useState({
    name: '',
    slug: '',
    description: '',
  });
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');

  const hasChinese = (text: string) => /[\u4e00-\u9fa5]/.test(text);

  const generateSlug = (name: string) => {
    if (hasChinese(name)) return '';
    return name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
  };

  const handleNameChange = (name: string) => {
    setForm(prev => ({ ...prev, name, slug: name }));
  };

  const handleNameBlur = () => {
    if (form.name) {
      const newSlug = generateSlug(form.name);
      if (newSlug) {
        setForm(prev => ({ ...prev, slug: newSlug }));
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const trimmedName = form.name.trim();
    if (!trimmedName) {
      setError('Name is required');
      return;
    }
    if (!/^[a-z0-9-]+$/.test(trimmedName)) {
      setError('Name can only contain lowercase letters, numbers, and hyphens');
      return;
    }

    setCreating(true);
    setError('');
    try {
      const trimmedDescription = form.description.trim();
      if (!trimmedDescription) {
        setError('Description is required');
        setCreating(false);
        return;
      }

      const data: CreateSkillRequest = {
        name: trimmedName,
        slug: trimmedName,
        description: trimmedDescription,
      };

      const newSkill = await api.post<Skill>('/skills', data);
      
      if (onSuccess) {
        onSuccess(newSkill);
      }
      
      onClose();
      setForm({ name: '', slug: '', description: '' });

      router.push(`/skills/${newSkill.id}`);
    } catch (err: unknown) {
      const errorMessage = parseApiError(err);
      const alreadyExistsMatch = errorMessage.match(/already exists/i);
      const slugMatch = errorMessage.match(/slug\s+['"]([^'"]+)['"]/i);

      if (alreadyExistsMatch && slugMatch) {
        setError(`Identifier "${slugMatch[1]}" already exists, please use a different identifier`);
      } else {
        setError(errorMessage);
      }
    } finally {
      setCreating(false);
    }
  };

  const handleClose = () => {
    if (!creating) {
      onClose();
      setForm({ name: '', slug: '', description: '' });
      setError('');
    }
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      title={t('createSkill')}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
            {error}
          </div>
        )}
        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 sm:mb-2">
            {tForm('name')}
          </label>
          <Input
            placeholder={tForm('namePlaceholder')}
            value={form.name}
            onChange={(e) => handleNameChange(e.target.value)}
            onBlur={handleNameBlur}
            required
            disabled={creating}
            autoFocus
            className="min-h-[44px]"
            title={tForm('nameHelp')}
          />
          <p className="mt-1.5 text-xs text-gray-500">
            {tForm('nameHelp')}
          </p>
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 sm:mb-2">
            {tForm('slug')}
          </label>
          <Input
            placeholder={tForm('slugPlaceholder')}
            value={form.slug}
            readOnly
            disabled={true}
            className="min-h-[44px] bg-gray-100 cursor-not-allowed"
          />
          <p className="mt-1.5 text-xs text-gray-500">
            {tForm('slugHelp')}
          </p>
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 sm:mb-2">
            {tForm('description')}
          </label>
          <Input
            placeholder={tForm('descriptionPlaceholder')}
            value={form.description}
            onChange={(e) => setForm(prev => ({ ...prev, description: e.target.value }))}
            disabled={creating}
            className="min-h-[44px]"
          />
        </div>

        <div className="flex flex-col gap-2 pt-2 sm:flex-row sm:gap-3">
          <Button
            type="button"
            variant="outline"
            className="min-h-[44px] flex-1"
            onClick={handleClose}
            disabled={creating}
          >
            {tCommon('cancel')}
          </Button>
          <Button
            type="submit"
            className="min-h-[44px] flex-1"
            disabled={creating || !form.name.trim() || !/^[a-z0-9-]+$/.test(form.name.trim()) || !form.description.trim()}
          >
            {creating ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                {tForm('creating')}
              </>
            ) : (
              tForm('createButton')
            )}
          </Button>
        </div>
      </form>
    </Dialog>
  );
}
