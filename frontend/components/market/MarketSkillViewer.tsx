'use client';

import { useTranslations } from 'next-intl';
import { FileText } from 'lucide-react';

import { useMarketFileTree } from '@/hooks/useMarketFileTree';
import { MarkdownViewer } from '@/components/editors/MarkdownViewer';
import { TextViewer } from '@/components/editors/TextViewer';
import { getFileType } from '@/lib/file-utils';
import { ImagePreview } from '@/components/file-tree/ImagePreview';
import { PdfPreview } from '@/components/file-tree/PdfPreview';

import { MarketSkillFileTree } from './MarketSkillFileTree';

interface MarketSkillViewerProps {
  sharedSkillId: string;
}

export function MarketSkillViewer({ sharedSkillId }: MarketSkillViewerProps) {
  const tEditor = useTranslations('editor');
  const { nodes, loading, error, selectedPath, selectedBlobId, toggleNode, selectNode } =
    useMarketFileTree({ sharedSkillId });

  const fileName = selectedPath.split('/').pop() || '';
  const fileType = fileName ? getFileType(fileName) : 'text';

  const renderPreview = () => {
    if (!selectedBlobId) {
      return (
        <div className="flex h-full flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-200 bg-white p-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-gray-100">
            <FileText className="h-7 w-7 text-gray-400" />
          </div>
          <h3 className="mt-4 text-base font-medium text-gray-900">{tEditor('selectFile')}</h3>
          <p className="mt-1 max-w-xs text-center text-sm text-gray-500">
            {tEditor('selectFileDesc')}
          </p>
        </div>
      );
    }

    const blobUrl = `/market/skills/${sharedSkillId}/blobs/${selectedBlobId}`;

    switch (fileType) {
      case 'image':
        return (
          <ImagePreview
            blobId={selectedBlobId}
            fileName={fileName}
            height="calc(100vh - 300px)"
            blobUrl={blobUrl}
          />
        );
      case 'pdf':
        return (
          <PdfPreview
            blobId={selectedBlobId}
            fileName={fileName}
            height="calc(100vh - 300px)"
            blobUrl={blobUrl}
          />
        );
      case 'markdown':
        return (
          <MarkdownViewer
            blobId={selectedBlobId}
            filePath={selectedPath}
            fileName={fileName}
            height="calc(100vh - 300px)"
            blobUrl={blobUrl}
          />
        );
      case 'text':
      default:
        return (
          <TextViewer
            blobId={selectedBlobId}
            filePath={selectedPath}
            fileName={fileName}
            height="calc(100vh - 300px)"
            blobUrl={blobUrl}
          />
        );
    }
  };

  return (
    <div className="flex h-[600px] gap-4 mt-6">
      <div className="w-64 shrink-0">
        <MarketSkillFileTree
          nodes={nodes}
          selectedPath={selectedPath}
          loading={loading}
          error={error}
          onSelect={selectNode}
          onToggle={toggleNode}
          sharedSkillId={sharedSkillId}
        />
      </div>
      <div className="flex-1 overflow-hidden">
        {renderPreview()}
      </div>
    </div>
  );
}
