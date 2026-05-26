'use client';

import { useCallback, useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';

import { Dialog } from '@/components/ui/Dialog';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { api } from '@/lib/api';
import { parseApiError } from '@/lib/errors';
import type { Category } from '@/types/market';

interface ShareSkillDialogProps {
  open: boolean;
  onClose: () => void;
  skillId: string;
  onSuccess?: () => void;
}

export function ShareSkillDialog({ open, onClose, skillId, onSuccess }: ShareSkillDialogProps) {
  const tCommon = useTranslations('common');
  const tMarket = useTranslations('market');

  const [categories, setCategories] = useState<Category[]>([]);
  const [form, setForm] = useState({
    category_id: '',
    share_message: '',
  });
  const [sharing, setSharing] = useState(false);
  const [error, setError] = useState('');
  const [loadingCategories, setLoadingCategories] = useState(false);

  const loadCategories = useCallback(async () => {
    setLoadingCategories(true);
    try {
      const response = await api.getCategories();
      setCategories(response.items);
      if (response.items.length > 0) {
        setForm((prev) => (
          prev.category_id ? prev : { ...prev, category_id: response.items[0].id }
        ));
      }
    } catch (err) {
      setError(parseApiError(err) || 'Failed to load categories');
    } finally {
      setLoadingCategories(false);
    }
  }, []);

  useEffect(() => {
    if (open && categories.length === 0) {
      void loadCategories();
    }
  }, [categories.length, loadCategories, open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!form.category_id) {
      setError('Please select a category');
      return;
    }

    setSharing(true);
    setError('');
    try {
      await api.shareSkill({
        skill_id: skillId,
        category_id: form.category_id,
        share_message: form.share_message.trim() || undefined,
      });

      if (onSuccess) onSuccess();
      
      handleClose();
    } catch (err: unknown) {
      setError(parseApiError(err) || 'Failed to share skill');
    } finally {
      setSharing(false);
    }
  };

  const handleClose = () => {
    if (!sharing) {
      onClose();
      setForm({ category_id: categories.length > 0 ? categories[0].id : '', share_message: '' });
      setError('');
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} title={tMarket('share_to_market')}>
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
            {error}
          </div>
        )}
        
        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 sm:mb-2">
            {tMarket('category_label')}
          </label>
          <select
            value={form.category_id}
            onChange={(e) => setForm((prev) => ({ ...prev, category_id: e.target.value }))}
            disabled={sharing || loadingCategories}
            className="flex min-h-[44px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            required
          >
            <option value="" disabled>{tMarket('select_category')}</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 sm:mb-2">
            {tMarket('share_message_label')}
          </label>
          <Input
            placeholder={tMarket('share_message_placeholder')}
            value={form.share_message}
            onChange={(e) => setForm((prev) => ({ ...prev, share_message: e.target.value }))}
            disabled={sharing}
            className="min-h-[44px]"
          />
        </div>

        <div className="flex flex-col gap-2 pt-2 sm:flex-row sm:gap-3">
          <Button
            type="button"
            variant="outline"
            className="min-h-[44px] flex-1"
            onClick={handleClose}
            disabled={sharing}
          >
            {tCommon('cancel')}
          </Button>
          <Button
            type="submit"
            className="min-h-[44px] flex-1"
            disabled={sharing || !form.category_id}
          >
            {sharing ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                {tMarket('sharing')}
              </>
            ) : (
              tMarket('share')
            )}
          </Button>
        </div>
      </form>
    </Dialog>
  );
}
