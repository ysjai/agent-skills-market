'use client';

import React from 'react';
import { Download } from 'lucide-react';
import { getFileType, type FileType } from '@/lib/file-utils';
import { ImagePreview } from './ImagePreview';
import { PdfPreview } from './PdfPreview';
import { MarkdownViewer } from '@/components/editors/MarkdownViewer';
import { TextViewer } from '@/components/editors/TextViewer';
import { getFileIcon } from '@/components/ui/FileIcons';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';

export interface FilePreviewProps {
  blobId?: string;
  treeId?: string;
  filePath?: string;
  initialContent?: string;
  fileName?: string;
  onSave?: (content: string, filePath: string, newBlobId?: string) => void;
  onChange?: (content: string) => void;
  onDownload?: () => void;
  className?: string;
  height?: string;
  readOnly?: boolean;
}

export function FilePreview({
  blobId,
  treeId,
  filePath,
  initialContent,
  fileName = 'untitled',
  onDownload,
  className,
  height = '500px',
}: FilePreviewProps) {
  const fileType: FileType = getFileType(fileName);

  const renderContent = () => {
    switch (fileType) {
      case 'image':
        return blobId ? (
          <ImagePreview
            blobId={blobId}
            fileName={fileName}
            height={height}
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            <span>No image data available</span>
          </div>
        );

      case 'pdf':
        return blobId ? (
          <PdfPreview
            blobId={blobId}
            fileName={fileName}
            height={height}
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            <span>No PDF data available</span>
          </div>
        );

      case 'markdown':
        return (
          <MarkdownViewer
            blobId={blobId}
            treeId={treeId}
            filePath={filePath}
            initialContent={initialContent}
            fileName={fileName}
            onDownload={onDownload}
            height={height}
          />
        );

      case 'text':
      default:
        return (
          <TextViewer
            blobId={blobId}
            filePath={filePath}
            initialContent={initialContent}
            fileName={fileName}
            onDownload={onDownload}
            height={height}
          />
        );
    }
  };

  const isViewerComponent = fileType === 'markdown' || fileType === 'text';

  return (
    <div
      className={cn(
        'flex flex-col overflow-hidden',
        !isViewerComponent && 'border border-gray-200 rounded-lg bg-white shadow-sm',
        className
      )}
    >
      {!isViewerComponent && (
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center gap-2">
            {getFileIcon(fileName, filePath)}
            <span className="text-sm font-medium text-gray-700">{fileName}</span>
          </div>
          {blobId && onDownload && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onDownload}
              className="h-8 px-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200"
              title="Download File"
            >
              <Download className="h-4 w-4" />
            </Button>
          )}
        </div>
      )}

      <div className="flex-1 overflow-hidden">
        {renderContent()}
      </div>
    </div>
  );
}

export default FilePreview;
