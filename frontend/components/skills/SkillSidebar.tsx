'use client';

import { useTranslations } from 'next-intl';
import { X } from 'lucide-react';

import { FileTree } from '@/components/file-tree/FileTree';
import type { FileTreeRef } from '@/components/file-tree/FileTree';
import type { Skill } from '@/types/skill';

interface SkillSidebarProps {
  skill: Skill;
  selectedFilePath: string;
  sidebarOpen: boolean;
  fileTreeRef?: React.RefObject<FileTreeRef | null>;
  onClose: () => void;
  onFileSelect: (path: string, blobId?: string) => void | Promise<boolean>;
  onFileReload: (path: string, newBlobId: string) => void;
  onFileDownload: (path: string, blobId: string, fileName: string) => void;
}

export function SkillSidebar({
  skill,
  selectedFilePath,
  sidebarOpen,
  fileTreeRef,
  onClose,
  onFileSelect,
  onFileReload,
  onFileDownload,
}: SkillSidebarProps) {
  const tFiles = useTranslations('files');

  return (
    <>
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 transform border-r border-gray-200 bg-white transition-transform duration-200 ease-in-out lg:static lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-14 items-center justify-between border-b border-gray-200 px-4 lg:hidden">
          <span className="font-semibold text-gray-900">{tFiles('title')}</span>
          <button
            onClick={onClose}
            className="flex h-9 w-9 items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-900"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <FileTree
          ref={fileTreeRef}
          treeId={skill.tree_id || undefined}
          onFileSelect={onFileSelect}
          selectedFilePath={selectedFilePath}
          onFileReload={onFileReload}
          onFileDownload={onFileDownload}
          className="h-[calc(100%-3.5rem)] border-0 shadow-none lg:h-full"
        />
      </aside>
    </>
  );
}
