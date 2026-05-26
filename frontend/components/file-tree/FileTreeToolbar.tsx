'use client';

import * as React from 'react';
import { useTranslations } from 'next-intl';
import { FilePlus, FolderPlus, Upload, FolderUp } from 'lucide-react';

import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';

interface FileTreeToolbarProps {
  onNewFile: () => void;
  onNewFolder: () => void;
  onUpload: () => void;
  onRefresh: () => void;
  className?: string;
}

export function FileTreeToolbar({
  onNewFile,
  onNewFolder,
  onUpload,
  onRefresh,
  className,
}: FileTreeToolbarProps) {
  const t = useTranslations('files');

  return (
    <div className={cn('flex items-center gap-1', className)}>
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8"
        onClick={onNewFile}
        title={t('newFile')}
      >
        <FilePlus className="h-4 w-4" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8"
        onClick={onNewFolder}
        title={t('newFolder')}
      >
        <FolderPlus className="h-4 w-4" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8"
        onClick={onUpload}
        title={t('uploadFiles')}
      >
        <Upload className="h-4 w-4" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8"
        onClick={onRefresh}
        title={t('uploadFolder')}
      >
        <FolderUp className="h-4 w-4" />
      </Button>
    </div>
  );
}
