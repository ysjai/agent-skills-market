'use client';

import { useEffect, useState, useCallback } from 'react';
import { useTranslations } from 'next-intl';

import { AppHeader } from '@/components/layout/AppHeader';
import { PromptList } from '@/components/prompts/PromptList';
import { PromptEditor } from '@/components/prompts/PromptEditor';
import { ImportDialog } from '@/components/prompts/ImportDialog';
import { ExportDialog } from '@/components/prompts/ExportDialog';
import { DeletePromptDialog } from '@/components/prompts/DeletePromptDialog';
import { SharePromptDialog } from '@/components/prompts/SharePromptDialog';
import { Button } from '@/components/ui/Button';
import { Dialog } from '@/components/ui/Dialog';
import { useToast } from '@/components/ui/Toast';
import { usePromptsStore } from '@/stores/promptsStore';
import { api } from '@/lib/api';
import { getCurrentUser, logout } from '@/app/api/auth';
import type { Prompt, PromptListResponse } from '@/types/prompt';
import type { User } from '@/types/user';

export default function PromptsPage() {
  const t = useTranslations('prompts');
  const tCommon = useTranslations('common');
  const tAuth = useTranslations('auth');
  const { showToast } = useToast();
  const [isMounted, setIsMounted] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const [exportContent, setExportContent] = useState('');
  const [showExport, setShowExport] = useState(false);
  const [deletePromptId, setDeletePromptId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isLogoutDialogOpen, setIsLogoutDialogOpen] = useState(false);
  const [isShareDialogOpen, setIsShareDialogOpen] = useState(false);
  const [sharePromptId, setSharePromptId] = useState<string>('');
  const [sharedSet, setSharedSet] = useState<Set<string>>(new Set());
  const {
    isLoading,
    setIsLoading,
    setErrorMessage,
    setPrompts,
    addPrompt,
    removePrompt,
    selectedPrompt,
    setSelectedPrompt,
    errorMessage
  } = usePromptsStore();

  useEffect(() => {
    loadPrompts();
    loadUser();
    const timer = setTimeout(() => setIsMounted(true), 50);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadPrompts = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const [data, sharedData] = await Promise.all([
        api.get<PromptListResponse>('/prompts'),
        api.getMySharedPrompts(0, 100).catch(() => ({ items: [], total: 0 })),
      ]);
      setPrompts(data.items);

      const newSharedSet = new Set<string>();
      sharedData.items.forEach(item => {
        if (item.prompt_id) {
          newSharedSet.add(item.prompt_id);
        }
      });
      setSharedSet(newSharedSet);
    } catch (error: unknown) {
      if (error instanceof Error && error.message.includes('404')) {
        setPrompts([]);
      } else {
        setErrorMessage(t('loadFailed'));
      }
    } finally {
      setIsLoading(false);
    }
  };

  const loadUser = async () => {
    try {
      const userData = await getCurrentUser();
      setUser(userData);
    } catch {
      // Silently ignore
    }
  };

  const handleLogout = () => {
    logout();
  };

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('.user-menu-container')) {
        setIsUserMenuOpen(false);
      }
    };
    if (isUserMenuOpen) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [isUserMenuOpen]);

  const handleImport = useCallback(async (content: string) => {
    const imported = await api.post<Prompt>('/prompts/import', { content });
    addPrompt(imported);
    setSelectedPrompt(imported);
  }, [addPrompt, setSelectedPrompt]);

  const handleExport = useCallback(async (promptId: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
      const resp = await fetch(`${apiUrl}/prompts/${promptId}/export`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      const text = await resp.text();
      setExportContent(text);
      setShowExport(true);
    } catch (err) {
      console.error('Failed to export prompt', err);
    }
  }, []);

  const handleDelete = useCallback((promptId: string) => {
    setDeletePromptId(promptId);
  }, []);

  const confirmDelete = useCallback(async () => {
    if (!deletePromptId) return;
    setIsDeleting(true);
    try {
      await api.delete(`/prompts/${deletePromptId}`);
      removePrompt(deletePromptId);
      if (selectedPrompt?.id === deletePromptId) {
        setSelectedPrompt(null);
      }
    } catch (err) {
      console.error('Failed to delete prompt', err);
    } finally {
      setIsDeleting(false);
      setDeletePromptId(null);
    }
  }, [deletePromptId, removePrompt, selectedPrompt, setSelectedPrompt]);

  const handleShareClick = useCallback((promptId: string) => {
    setSharePromptId(promptId);
    setIsShareDialogOpen(true);
  }, []);

  const handleUnshareClick = useCallback(async (promptId: string) => {
    try {
      await api.unsharePrompt(promptId);
      setSharedSet(prev => {
        const next = new Set(prev);
        next.delete(promptId);
        return next;
      });
      showToast(t('unshare_success'), 'success');
    } catch {
      showToast(tCommon('failed'), 'error');
    }
  }, [showToast, t, tCommon]);

  const handleShareSuccess = useCallback(() => {
    showToast(t('share_success'), 'success');
    loadPrompts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showToast, t]);

  return (
    <div className={`flex h-screen flex-col bg-gray-50 transition-opacity duration-500 ${isMounted ? 'opacity-100' : 'opacity-0'}`}>
      <AppHeader
        user={user}
        isUserMenuOpen={isUserMenuOpen}
        onUserMenuToggle={() => setIsUserMenuOpen(!isUserMenuOpen)}
        onLogoutClick={() => setIsLogoutDialogOpen(true)}
      />

      {errorMessage && (
        <div className="mx-auto mt-4 w-full max-w-7xl px-4 sm:px-6 shrink-0">
          <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-800 shadow-sm">
            {errorMessage}
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="flex flex-1 items-center justify-center animate-fade-in">
          <div className="flex items-center gap-2 text-gray-500 bg-white px-6 py-4 rounded-full shadow-sm">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-gray-900" />
            <span className="font-medium">{tCommon('loading')}</span>
          </div>
        </div>
      ) : (
        <div className="flex flex-1 overflow-hidden">
          <PromptList
            onImportClick={() => setShowImport(true)}
            onExportClick={handleExport}
            onDeleteClick={handleDelete}
            onShareClick={handleShareClick}
            onUnshareClick={handleUnshareClick}
            sharedSet={sharedSet}
          />
          <PromptEditor />
        </div>
      )}

      <ImportDialog
        isOpen={showImport}
        onClose={() => setShowImport(false)}
        onImport={handleImport}
      />

      <ExportDialog
        isOpen={showExport}
        onClose={() => setShowExport(false)}
        content={exportContent}
        promptTitle={selectedPrompt?.title}
      />

      <DeletePromptDialog
        open={deletePromptId !== null}
        onClose={() => setDeletePromptId(null)}
        onConfirm={confirmDelete}
        isLoading={isDeleting}
      />

      <SharePromptDialog
        open={isShareDialogOpen}
        onClose={() => setIsShareDialogOpen(false)}
        promptId={sharePromptId}
        onSuccess={handleShareSuccess}
      />

      <Dialog
        open={isLogoutDialogOpen}
        onClose={() => setIsLogoutDialogOpen(false)}
        title={tAuth('signOut')}
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600 sm:text-base">
            {tAuth('logoutConfirm')}
          </p>
          <div className="flex flex-col gap-2 sm:flex-row sm:gap-3">
            <Button
              variant="outline"
              className="min-h-[44px] flex-1"
              onClick={() => setIsLogoutDialogOpen(false)}
            >
              {tCommon('cancel')}
            </Button>
            <Button
              variant="default"
              className="min-h-[44px] flex-1 bg-gray-900 hover:bg-gray-800 text-white"
              onClick={handleLogout}
            >
              {tAuth('signOut')}
            </Button>
          </div>
        </div>
      </Dialog>
    </div>
  );
}
