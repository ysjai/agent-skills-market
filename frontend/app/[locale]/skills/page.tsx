'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import { useRouter } from '@/i18n/routing';
import { useTranslations } from 'next-intl';
import { FolderGit2, FolderUp } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { Dialog } from '@/components/ui/Dialog';
import { CreateSkillDialog } from '@/components/skills/CreateSkillDialog';
import { DeleteSkillDialog } from '@/components/skills/DeleteSkillDialog';
import { ImportSkillDialog } from '@/components/skills/ImportSkillDialog';
import { SkillsPageHeader } from '@/components/skills/SkillsPageHeader';
import { SkillCard } from '@/components/skills/SkillCard';
import { TopNav } from '@/components/layout/TopNav';
import { api } from '@/lib/api';
import type { Skill, SkillListResponse } from '@/types/skill';
import { getErrorMessage } from '@/lib/errors';
import { logout } from '@/app/api/auth';
import { getCurrentUser } from '@/app/api/auth';
import type { User } from '@/types/user';
import { DownloadDialog } from '@/components/misc/DownloadDialog';

export default function SkillsPage() {
  const t = useTranslations('skills');
  const tCommon = useTranslations('common');
  const tAuth = useTranslations('auth');
  const router = useRouter();
  const [skills, setSkills] = useState<Skill[]>([]);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState('');
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  const [isLogoutDialogOpen, setIsLogoutDialogOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  const [isImportDialogOpen, setIsImportDialogOpen] = useState(false);
  const [isDownloadDialogOpen, setIsDownloadDialogOpen] = useState(false);
  const [downloadSkillId, setDownloadSkillId] = useState<string>('');
  const [downloadSkillName, setDownloadSkillName] = useState<string>('');



  useEffect(() => {
    loadSkills();
    loadUser();
    const timer = setTimeout(() => setIsMounted(true), 50);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('.menu-container')) {
        setOpenMenuId(null);
      }
      if (!target.closest('.user-menu-container')) {
        setIsUserMenuOpen(false);
      }
    };
    if (openMenuId || isUserMenuOpen) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [openMenuId, isUserMenuOpen]);

  const loadSkills = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await api.get<SkillListResponse>('/skills');
      setSkills(data.items);
    } catch {
      setError(t('errors.loadFailed') || 'Failed to load skills');
    } finally {
      setIsLoading(false);
    }
  };

  const loadUser = async () => {
    try {
      const userData = await getCurrentUser();
      setUser(userData);
    } catch {
      // Silently ignore user load errors
    }
  };

  const handleLogout = () => {
    logout();
  };

  const handleDeleteSkill = async (skillId: string) => {
    setDeletingId(skillId);
    setDeleteError('');
    try {
      await api.delete(`/skills/${skillId}`);
      setSkills(prev => prev.filter(s => s.id !== skillId));
      setDeleteConfirmId(null);
      setOpenMenuId(null);
    } catch (err) {
      setDeleteError(getErrorMessage(err, 'Failed to delete skill'));
    } finally {
      setDeletingId(null);
    }
  };

  const filteredSkills = useMemo(() => {
    if (!searchQuery) return skills;
    const query = searchQuery.toLowerCase();
    return skills.filter(skill => 
      skill.name.toLowerCase().includes(query) ||
      skill.description?.toLowerCase().includes(query)
    );
  }, [skills, searchQuery]);

  const handleMenuToggle = useCallback((skillId: string | null) => {
    setOpenMenuId(openMenuId === skillId ? null : skillId);
  }, [openMenuId]);

  const handleDownload = useCallback((skillId: string, skillName: string) => {
    setDownloadSkillId(skillId);
    setDownloadSkillName(skillName);
    setIsDownloadDialogOpen(true);
    setOpenMenuId(null);
  }, []);

  const handleDelete = useCallback((skillId: string) => {
    setDeleteConfirmId(skillId);
    setOpenMenuId(null);
  }, []);

  const handleNavigate = useCallback((skillId: string) => {
    router.push(`/skills/${skillId}`);
  }, [router]);

  return (
    <div className={`flex min-h-screen flex-col bg-gradient-subtle transition-opacity duration-500 ${isMounted ? 'opacity-100' : 'opacity-0'}`}>
      <TopNav />
      <SkillsPageHeader
        user={user}
        skillsCount={skills.length}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onCreateClick={() => setIsCreateDialogOpen(true)}
        onImportClick={() => setIsImportDialogOpen(true)}
        isUserMenuOpen={isUserMenuOpen}
        onUserMenuToggle={() => setIsUserMenuOpen(!isUserMenuOpen)}
        onLogoutClick={() => setIsLogoutDialogOpen(true)}
      />

      <main className="flex-1 p-4 sm:p-6">
        <div className="mx-auto max-w-7xl">
          {error && (
            <div className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-800">
              {error}
            </div>
          )}

          {isLoading ? (
            <div className="flex items-center justify-center py-20 animate-fade-in">
              <div className="flex items-center gap-2 text-gray-500">
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-gray-900" />
                <span>{tCommon('loading')}</span>
              </div>
            </div>
          ) : filteredSkills.length === 0 ? (
            <Card className="border-dashed animate-scale-in">
              <CardContent className="flex flex-col items-center justify-center px-4 py-12 text-center sm:py-20">
                <div className="flex h-14 w-14 items-center justify-center rounded-full bg-gray-100 sm:h-16 sm:w-16">
                  <FolderGit2 className="h-7 w-7 text-gray-400 sm:h-8 sm:w-8" />
                </div>
                <h3 className="mt-4 text-base font-medium text-gray-900 sm:text-lg">
                  {searchQuery ? t('noSkillsFound') : t('noSkills')}
                </h3>
                <p className="mt-1 max-w-xs text-sm text-gray-500 sm:max-w-sm">
                  {searchQuery
                    ? t('tryAdjustSearch')
                    : t('createFirst')}
                </p>
                {!searchQuery && (
                  <Button
                    onClick={() => setIsImportDialogOpen(true)}
                    className="mt-6 min-h-[44px]"
                  >
                    <FolderUp className="mr-2 h-4 w-4" />
                    {t('importSkill')}
                  </Button>
                )}
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 animate-fade-in-scale items-stretch">
              {filteredSkills.map((skill) => (
                <SkillCard
                  key={skill.id}
                  skill={skill}
                  openMenuId={openMenuId}
                  onMenuToggle={handleMenuToggle}
                  onDownload={handleDownload}
                  onDelete={handleDelete}
                  onNavigate={handleNavigate}
                />
              ))}
            </div>
          )}
        </div>
      </main>

      <CreateSkillDialog
        open={isCreateDialogOpen}
        onClose={() => setIsCreateDialogOpen(false)}
        onSuccess={(skill) => setSkills(prev => [skill, ...prev])}
      />

      <DeleteSkillDialog
        open={!!deleteConfirmId}
        onClose={() => setDeleteConfirmId(null)}
        onConfirm={() => deleteConfirmId && handleDeleteSkill(deleteConfirmId)}
        deleting={!!deletingId}
        error={deleteError}
        title={t('deleteSkill')}
        message={t('deleteConfirm')}
      />

      <ImportSkillDialog
        open={isImportDialogOpen}
        onClose={() => setIsImportDialogOpen(false)}
        onSuccess={(skill) => setSkills(prev => [skill, ...prev])}
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
              variant="destructive"
              className="min-h-[44px] flex-1"
              onClick={handleLogout}
            >
              {tAuth('signOut')}
            </Button>
          </div>
        </div>
      </Dialog>

      <DownloadDialog
        open={isDownloadDialogOpen}
        skillId={downloadSkillId}
        skillName={downloadSkillName}
        onClose={() => setIsDownloadDialogOpen(false)}
        onSuccess={() => {}}
      />
    </div>
  );
}
