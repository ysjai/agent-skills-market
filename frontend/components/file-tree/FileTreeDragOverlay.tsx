'use client';

import * as React from 'react';
import { useTranslations } from 'next-intl';
import { Upload } from 'lucide-react';

interface FileTreeDragOverlayProps {
  isDragging: boolean;
}

export function FileTreeDragOverlay({ isDragging }: FileTreeDragOverlayProps) {
  const t = useTranslations('files');

  if (!isDragging) {
    return null;
  }

  return (
    <div className="mb-4 rounded-lg border-2 border-dashed border-blue-500 bg-blue-50 p-6 text-center">
      <Upload className="mx-auto h-8 w-8 text-blue-500" />
      <p className="mt-2 text-sm text-blue-600">{t('releaseToUpload')}</p>
    </div>
  );
}
