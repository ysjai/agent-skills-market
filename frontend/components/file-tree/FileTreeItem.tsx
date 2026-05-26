'use client';

import * as React from 'react';
import { memo } from 'react';
import { useTranslations } from 'next-intl';
import {
  ChevronRight,
  ChevronDown,
  Folder,
  FolderOpen,
  MoreVertical,
  Trash2,
  Edit3,
  FilePlus,
  FolderPlus,
  Download,
  Upload,
  FolderUp,
} from 'lucide-react';

import { cn } from '@/lib/utils';
import { getFileIcon } from '@/components/ui/FileIcons';
import { Input } from '@/components/ui/Input';
import type { FileTreeNode } from '@/types/file-tree';
import { hasWindowsReservedChars } from '@/lib/windows-fs';

interface FileTreeItemProps {
  node: FileTreeNode;
  onToggle: (node: FileTreeNode) => void;
  onSelect: (node: FileTreeNode) => void;
  onAddFile: (parentPath: string) => void;
  onAddFolder: (parentPath: string) => void;
  onDelete: (path: string) => void;
  onRename: (path: string, newName: string) => Promise<boolean>;
  onMove: (source: string, targetDir: string) => void;
  onDragStart: (path: string) => void;
  onDragOver: (path: string | null) => void;
  dragSource?: string | null;
  dragOverTarget?: string | null;
  selectedPath?: string;
  onDownload?: (path: string, blobId: string, fileName: string) => void;
  onDownloadFolder?: (folderPath: string, folderName: string) => void;
  onUploadFile?: (folderPath: string) => void;
  onUploadFolder?: (folderPath: string) => void;
}

export const FileTreeItem = memo(function FileTreeItem({
  node,
  onToggle,
  onSelect,
  onAddFile,
  onAddFolder,
  onDelete,
  onRename,
  onMove,
  onDragStart,
  onDragOver,
  dragSource,
  dragOverTarget,
  selectedPath,
  onDownload,
  onDownloadFolder,
  onUploadFile,
  onUploadFolder,
}: FileTreeItemProps) {
  const t = useTranslations('files');
  const tCommon = useTranslations('common');
  const [isRenaming, setIsRenaming] = React.useState(false);
  const [renameValue, setRenameValue] = React.useState(node.name || '');
  const [renameError, setRenameError] = React.useState<string | null>(null);
  const [renameWarning, setRenameWarning] = React.useState<string | null>(null);
  const [isRenamingLoading, setIsRenamingLoading] = React.useState(false);
  const [showMenu, setShowMenu] = React.useState(false);
  const menuRef = React.useRef<HTMLDivElement>(null);
  const inputRef = React.useRef<HTMLInputElement>(null);

  const isSelected = selectedPath === node.path;
  const isDirectory = node.type === 'tree';

  // Focus input when renaming starts
  React.useEffect(() => {
    if (isRenaming && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isRenaming]);

  // Close menu when clicking outside
  React.useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowMenu(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (isDirectory) {
      onToggle(node);
    }
  };

  const handleSelect = () => {
    onSelect(node);
  };

  const handleDoubleClick = () => {
    if (isDirectory) {
      onToggle(node);
    }
  };

  const handleRenameSubmit = async () => {
    const trimmedValue = renameValue?.trim();
    if (!trimmedValue) {
      setIsRenaming(false);
      setRenameError(null);
      setRenameWarning(null);
      return;
    }
    if (trimmedValue === node.name) {
      setIsRenaming(false);
      setRenameError(null);
      setRenameWarning(null);
      return;
    }

    setIsRenamingLoading(true);
    setRenameError(null);
    setRenameWarning(null);

    const parentPath = node.path.includes('/')
      ? node.path.substring(0, node.path.lastIndexOf('/') + 1)
      : '';
    const newPath = parentPath + trimmedValue;

    try {
      const success = await onRename(node.path, newPath);
      if (success) {
        setIsRenaming(false);
        setRenameError(null);
      } else {
        setRenameError(t('alreadyExists'));
      }
    } catch (err) {
      setRenameError(err instanceof Error ? err.message : t('renameFailed'));
    } finally {
      setIsRenamingLoading(false);
    }
  };

  const handleRenameCancel = () => {
    setIsRenaming(false);
    setRenameValue(node.name || '');
    setRenameError(null);
    setRenameWarning(null);
  };

  const handleRenameKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isRenamingLoading) {
      handleRenameSubmit();
    } else if (e.key === 'Escape') {
      handleRenameCancel();
    }
  };

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setShowMenu(true);
  };

  const handleDragStart = (e: React.DragEvent) => {
    e.dataTransfer.setData('text/plain', node.path);
    e.dataTransfer.effectAllowed = 'move';
    onDragStart(node.path);
  };

  const handleDragOver = (e: React.DragEvent) => {
    if (isDirectory && dragSource && dragSource !== node.path) {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
      onDragOver(node.path);
    }
  };

  const handleDragLeave = () => {
    onDragOver(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (isDirectory && dragSource && dragSource !== node.path) {
      onMove(dragSource, node.path);
    }
    onDragOver(null);
  };

  const icon = isDirectory ? (
    node.isExpanded ? (
      <FolderOpen className="h-4 w-4 text-black" />
    ) : (
      <Folder className="h-4 w-4 text-black" />
    )
  ) : (
    getFileIcon(node.name || '', node.path)
  );

  return (
    <div className="select-none">
      <div
        className={cn(
          'group flex items-center gap-1 rounded-md py-1.5 pr-2 transition-colors',
          'hover:bg-gray-100',
          isSelected && 'bg-slate-200 text-slate-900 hover:bg-slate-300',
          !isSelected && 'text-gray-700',
          isDirectory && dragOverTarget === node.path && 'bg-blue-100 ring-2 ring-blue-400'
        )}
        style={{ paddingLeft: `${node.depth * 16 + 8}px` }}
        onClick={handleSelect}
        onDoubleClick={handleDoubleClick}
        onContextMenu={handleContextMenu}
        draggable={!isRenaming}
        onDragStart={handleDragStart}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {/* Expand/Collapse button */}
        <button
          onClick={handleToggle}
          className={cn(
            'flex h-5 w-5 items-center justify-center rounded transition-opacity',
            !isDirectory && 'opacity-0',
            isSelected ? 'text-slate-500 hover:text-slate-800' : 'text-gray-400 hover:text-gray-600'
          )}
          disabled={!isDirectory}
        >
          {node.isExpanded ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
        </button>

        {/* File/Folder icon */}
        <span className="flex-shrink-0">{icon}</span>

        {/* Name (editable when renaming) */}
        {isRenaming ? (
          <div className="flex flex-1 flex-col" onClick={(e) => e.stopPropagation()}>
            <Input
              ref={inputRef}
              value={renameValue}
              onChange={(e) => {
                const value = e.target.value;
                setRenameValue(value);
                setRenameError(null);
                if (hasWindowsReservedChars(value)) {
                  setRenameWarning(t('windowsIncompatibleChars'));
                } else {
                  setRenameWarning(null);
                }
              }}
              onKeyDown={handleRenameKeyDown}
              onBlur={handleRenameSubmit}
              className={cn(
                'h-6 py-0 text-sm',
                renameError && 'border-red-500 focus:ring-red-500',
                renameWarning && !renameError && 'border-yellow-500 focus:ring-yellow-500'
              )}
              disabled={isRenamingLoading}
            />
            {renameError && (
              <span className="mt-0.5 text-xs text-red-500">{renameError}</span>
            )}
            {renameWarning && !renameError && (
              <span className="mt-0.5 text-xs text-yellow-600">{renameWarning}</span>
            )}
          </div>
        ) : (
          <span
            className={cn(
              'flex-1 truncate text-sm',
              isSelected ? 'text-slate-900' : 'text-gray-700'
            )}
          >
            {node.name}
          </span>
        )}

        {/* Context menu trigger */}
        {!isRenaming && (
          <div className="relative" ref={menuRef}>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowMenu(!showMenu);
              }}
              className={cn(
                'flex h-6 w-6 items-center justify-center rounded opacity-0 transition-opacity group-hover:opacity-100',
                isSelected
                  ? 'text-slate-500 hover:bg-slate-300 hover:text-slate-700'
                  : 'text-gray-400 hover:bg-gray-200 hover:text-gray-700',
                showMenu && 'opacity-100'
              )}
            >
              <MoreVertical className="h-4 w-4" />
            </button>

            {/* Dropdown menu */}
            {showMenu && (
              <div
                className={cn(
                  'absolute right-0 top-full z-50 mt-1 min-w-[160px] rounded-lg border py-1 shadow-lg',
                  'border-gray-200 bg-white'
                )}
                onClick={(e) => e.stopPropagation()}
              >
                {isDirectory && (
                  <>
                    <button
                      onClick={() => {
                        onAddFile(node.path);
                        setShowMenu(false);
                      }}
                      className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-gray-700 transition-colors hover:bg-gray-100"
                    >
                      <FilePlus className="h-4 w-4" />
                      {t('newFile')}
                    </button>
                    <button
                      onClick={() => {
                        onAddFolder(node.path);
                        setShowMenu(false);
                      }}
                      className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-gray-700 transition-colors hover:bg-gray-100"
                    >
                      <FolderPlus className="h-4 w-4" />
                      {t('newFolder')}
                    </button>
                    <button
                      onClick={() => {
                        onUploadFile?.(node.path);
                        setShowMenu(false);
                      }}
                      className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-gray-700 transition-colors hover:bg-gray-100"
                    >
                      <Upload className="h-4 w-4" />
                      {t('uploadFile')}
                    </button>
                    <button
                      onClick={() => {
                        onUploadFolder?.(node.path);
                        setShowMenu(false);
                      }}
                      className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-gray-700 transition-colors hover:bg-gray-100"
                    >
                      <FolderUp className="h-4 w-4" />
                      {t('uploadFolder')}
                    </button>
                    <button
                      onClick={() => {
                        onDownloadFolder?.(node.path, node.name || 'folder');
                        setShowMenu(false);
                      }}
                      className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-gray-700 transition-colors hover:bg-gray-100"
                    >
                      <Download className="h-4 w-4" />
                      {t('downloadFolder')}
                    </button>
                    <div className="my-1 h-px bg-gray-200" />
                  </>
                )}
                {!isDirectory && node.blob_id && onDownload && (
                  <button
                    onClick={() => {
                      onDownload(node.path, node.blob_id || '', node.name || '');
                      setShowMenu(false);
                    }}
                    className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-gray-700 transition-colors hover:bg-gray-100"
                  >
                    <Download className="h-4 w-4" />
                    {t('download')}
                  </button>
                )}
                <button
                  onClick={() => {
                    setIsRenaming(true);
                    setRenameWarning(null);
                    setShowMenu(false);
                  }}
                  className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-gray-700 transition-colors hover:bg-gray-100"
                >
                  <Edit3 className="h-4 w-4" />
                  {t('rename')}
                </button>
                <button
                  onClick={() => {
                    onDelete(node.path);
                    setShowMenu(false);
                  }}
                  className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-red-600 transition-colors hover:bg-red-50"
                >
                  <Trash2 className="h-4 w-4" />
                  {tCommon('delete')}
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Render children */}
      {isDirectory && node.isExpanded && node.children && (
        <div className="mt-0.5">
            {node.children.map((child) => (
              <FileTreeItem
                key={child.id}
                node={child}
                onToggle={onToggle}
                onSelect={onSelect}
                onAddFile={onAddFile}
                onAddFolder={onAddFolder}
                onDelete={onDelete}
                onRename={onRename}
                onMove={onMove}
                onDragStart={onDragStart}
                onDragOver={onDragOver}
                dragSource={dragSource}
                dragOverTarget={dragOverTarget}
                selectedPath={selectedPath}
                onDownload={onDownload}
                onDownloadFolder={onDownloadFolder}
                onUploadFile={onUploadFile}
                onUploadFolder={onUploadFolder}
              />
            ))}
        </div>
      )}
    </div>
  );
});

FileTreeItem.displayName = 'FileTreeItem';
