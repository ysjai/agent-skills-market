'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from '@/i18n/routing';
import { useParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { DownloadDialog } from '@/components/misc/DownloadDialog';
import { SkillHeader } from '@/components/skills/SkillHeader';
import { DeleteConfirmDialog } from '@/components/skills/DeleteConfirmDialog';
import { SkillSidebar } from '@/components/skills/SkillSidebar';
import { SkillEditorArea } from '@/components/skills/SkillEditorArea';
import { LoadingState, ErrorState } from '@/components/skills/SkillPageStates';
import { api } from '@/lib/api';
import type { Skill } from '@/types/skill';
import type { FileTreeRef } from '@/components/file-tree/FileTree';
import { useToast } from '@/components/ui/Toast';

export default function SkillDetailPage() {
  const t = useTranslations('skills');
  const tCommon = useTranslations('common');
  const router = useRouter();
  const params = useParams();
  const skillId = params.id as string;

  const [skill, setSkill] = useState<Skill | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedFilePath, setSelectedFilePath] = useState<string>('');
  const [selectedBlobId, setSelectedBlobId] = useState<string>('');
  const [_activeTab, setActiveTab] = useState<'editor' | 'versions'>('editor');
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [downloadDialogOpen, setDownloadDialogOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const fileTreeRef = useRef<FileTreeRef>(null);
  const { showToast } = useToast();

  const handleFileSelect = async (path: string, blobId?: string): Promise<boolean> => {
    if (path === selectedFilePath) {
      return true;
    }

    setSelectedFilePath(path);
    setSelectedBlobId(blobId || '');
    setActiveTab('editor');
    setSidebarOpen(false);
    return true;
  };

  useEffect(() => {
    if (skillId) {
      loadSkill();
    }
    const timer = setTimeout(() => setMounted(true), 50);
    return () => clearTimeout(timer);
  }, [skillId]);

  const loadSkill = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.get<Skill>(`/skills/${skillId}`);
      setSkill(data);
    } catch {
      setError('Failed to load skill');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!skill) return;
    setDeleting(true);
    try {
      await api.delete(`/skills/${skill.id}`);
      router.push('/skills');
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Failed to delete skill', 'error');
    } finally {
      setDeleting(false);
      setDeleteConfirmOpen(false);
    }
  };

  const handleDownload = async (_path: string, blobId: string, fileName: string) => {
    if (!blobId) return showToast('Unable to download: file content unavailable', 'error');
    const blob = await api.getBlob(`/blobs/${blobId}`);
    const url = window.URL.createObjectURL(blob);
    const downloadLink = document.createElement('a');
    downloadLink.href = url;
    downloadLink.download = fileName;
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
    window.URL.revokeObjectURL(url);
  };

  const handleFilePreviewDownload = () => {
    if (selectedBlobId && selectedFilePath) {
      const fileName = selectedFilePath.split('/').pop() || 'download';
      handleDownload(selectedFilePath, selectedBlobId, fileName);
    }
  };

  if (loading) {
    return <LoadingState tCommon={tCommon} />;
  }

  if (error || !skill) {
    return <ErrorState error={error} t={t} tCommon={tCommon} />;
  }

  return (
    <div className={`flex h-screen flex-col bg-gradient-subtle transition-opacity duration-500 ${mounted ? 'opacity-100' : 'opacity-0'}`}>
      <SkillHeader
        skill={skill}
        isUserMenuOpen={isUserMenuOpen}
        onDownload={() => setDownloadDialogOpen(true)}
        onDelete={() => setDeleteConfirmOpen(true)}
        onToggleSidebar={() => setSidebarOpen(true)}
        onUserMenuToggle={() => setIsUserMenuOpen(!isUserMenuOpen)}
        onNavigate={(path: string, options?: { locale?: string }) => { router.push(path, options); }}
      />

      <div className="flex flex-1 overflow-hidden">
        <SkillSidebar
          skill={skill}
          selectedFilePath={selectedFilePath}
          sidebarOpen={sidebarOpen}
          fileTreeRef={fileTreeRef}
          onClose={() => setSidebarOpen(false)}
          onFileSelect={handleFileSelect}
          onFileReload={(_, newBlobId) => setSelectedBlobId(newBlobId)}
          onFileDownload={handleDownload}
        />

        <SkillEditorArea
          skill={skill}
          selectedFilePath={selectedFilePath}
          selectedBlobId={selectedBlobId}
          onOpenSidebar={() => setSidebarOpen(true)}
          onFileDownload={handleFilePreviewDownload}
        />
      </div>

      <DeleteConfirmDialog
        open={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
        onConfirm={handleDelete}
        isLoading={deleting}
      />

      {skill && (
        <DownloadDialog
          open={downloadDialogOpen}
          skillId={skill.id}
          skillName={skill.name}
          onClose={() => setDownloadDialogOpen(false)}
          onSuccess={() => {}}
        />
      )}
    </div>
  );
}
