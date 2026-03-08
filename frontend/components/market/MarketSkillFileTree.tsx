'use client';

import { useTranslations } from 'next-intl';
import { FolderTree, ChevronRight, ChevronDown, Folder, FolderOpen, Download } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import type { MarketFileNode } from '@/hooks/useMarketFileTree';
import { getFileIcon } from '@/components/ui/FileIcons';
import { api } from '@/lib/api';

interface MarketSkillFileTreeProps {
  nodes: MarketFileNode[];
  selectedPath: string;
  loading: boolean;
  error: string | null;
  onSelect: (path: string, blobId?: string) => void;
  onToggle: (path: string) => void;
  sharedSkillId: string;
  className?: string;
}

function FileTreeNode({
  node,
  selectedPath,
  onSelect,
  onToggle,
  sharedSkillId,
}: {
  node: MarketFileNode;
  selectedPath: string;
  onSelect: (path: string, blobId?: string) => void;
  onToggle: (path: string) => void;
  sharedSkillId: string;
}) {
  const isSelected = node.path === selectedPath;
  const isFolder = node.type === 'tree';

  const handleDownloadFile = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!node.blob_id) return;
    try {
      const blob = await api.getMarketSkillBlob(sharedSkillId, node.blob_id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = node.name;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download file:', err);
    }
  };

  return (
    <div>
      <div className="group relative flex items-center">
        <button
          onClick={() => {
            if (isFolder) {
              onToggle(node.path);
            } else {
              onSelect(node.path, node.blob_id);
            }
          }}
          className={cn(
            'flex w-full items-center gap-1.5 rounded-md px-2 py-1.5 text-left text-sm transition-colors',
            isSelected
              ? 'bg-blue-50 text-blue-700'
              : 'text-gray-700 hover:bg-gray-50'
          )}
          style={{ paddingLeft: `${node.depth * 16 + 8}px` }}
        >
          {isFolder ? (
            <>
              {node.isExpanded ? (
                <ChevronDown className="h-3.5 w-3.5 shrink-0 text-gray-400" />
              ) : (
                <ChevronRight className="h-3.5 w-3.5 shrink-0 text-gray-400" />
              )}
              {node.isExpanded ? (
                <FolderOpen className="h-4 w-4 shrink-0 text-amber-500" />
              ) : (
                <Folder className="h-4 w-4 shrink-0 text-amber-500" />
              )}
            </>
          ) : (
            <>
              <span className="h-3.5 w-3.5 shrink-0" />
              {getFileIcon(node.name, node.path)}
            </>
          )}
          <span className="truncate">{node.name}</span>
        </button>
        {!isFolder && node.blob_id && (
          <button
            onClick={handleDownloadFile}
            className="absolute right-1 opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-200 rounded transition-opacity"
            title="Download file"
          >
            <Download className="h-3.5 w-3.5 text-gray-500" />
          </button>
        )}
      </div>

      {isFolder && node.isExpanded && node.children.length > 0 && (
        <div>
          {node.children.map((child) => (
            <FileTreeNode
              key={child.path}
              node={child}
              selectedPath={selectedPath}
              onSelect={onSelect}
              onToggle={onToggle}
              sharedSkillId={sharedSkillId}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function MarketSkillFileTree({
  nodes,
  selectedPath,
  loading,
  error,
  onSelect,
  onToggle,
  sharedSkillId,
  className,
}: MarketSkillFileTreeProps) {
  const t = useTranslations('files');

  if (loading) {
    return (
      <Card className={cn('h-full', className)}>
        <CardContent className="flex h-full items-center justify-center p-8">
          <p className="text-gray-500">{t('loading')}</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={cn('h-full', className)}>
        <CardContent className="flex h-full items-center justify-center p-8">
          <p className="text-red-500">{error}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn('flex h-full flex-col', className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
        <CardTitle className="flex items-center gap-2 text-base font-semibold">
          <FolderTree className="h-5 w-5 text-gray-600" />
          {t('title')}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-auto py-2">
        {nodes.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <FolderTree className="h-12 w-12 text-gray-300" />
            <p className="mt-2 text-sm text-gray-500">{t('noFiles')}</p>
          </div>
        ) : (
          <div className="space-y-0.5">
            {nodes.map((node) => (
              <FileTreeNode
                key={node.path}
                node={node}
                selectedPath={selectedPath}
                onSelect={onSelect}
                onToggle={onToggle}
                sharedSkillId={sharedSkillId}
              />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
