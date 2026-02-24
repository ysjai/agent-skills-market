'use client';

import { useTranslations } from 'next-intl';
import { FileText, Menu } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { FilePreview } from '@/components/file-tree/FilePreview';
import type { Skill } from '@/types/skill';

interface SkillEditorAreaProps {
  skill: Skill;
  selectedFilePath: string;
  selectedBlobId: string;
  onOpenSidebar: () => void;
  onFileDownload: () => void;
}

export function SkillEditorArea({
  skill,
  selectedFilePath,
  selectedBlobId,
  onOpenSidebar,
  onFileDownload,
}: SkillEditorAreaProps) {
  const tEditor = useTranslations('editor');

  return (
    <main className="flex flex-1 overflow-hidden">
      <div className="flex flex-1 flex-col p-3 sm:p-4">
          {selectedBlobId ? (
            <div className="flex h-full flex-col">
              <div className="flex-1">
                <FilePreview
                  blobId={selectedBlobId}
                  treeId={skill?.tree_id || ''}
                  filePath={selectedFilePath}
                  fileName={selectedFilePath.split('/').pop() || 'untitled.md'}
                  height="calc(100vh - 180px)"
                  onDownload={onFileDownload}
                />
              </div>
            </div>
          ) : (
            <div className="flex h-full flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-200 bg-white p-4 animate-fade-in-up">
              <div className="flex h-14 w-14 items-center justify-center rounded-full bg-gray-100 sm:h-16 sm:w-16">
                <FileText className="h-7 w-7 text-gray-400 sm:h-8 sm:w-8" />
              </div>
              <h3 className="mt-4 text-base font-medium text-gray-900 sm:text-lg">{tEditor('selectFile')}</h3>
              <p className="mt-1 max-w-xs text-center text-sm text-gray-500">
                {tEditor('selectFileDesc')}
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={onOpenSidebar}
                className="mt-4 lg:hidden btn-interactive"
              >
                <Menu className="mr-2 h-4 w-4" />
                {tEditor('openFileTree')}
              </Button>
            </div>
          )}
        </div>
    </main>
  );
}
