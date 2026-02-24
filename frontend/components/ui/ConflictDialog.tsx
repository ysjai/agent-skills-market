'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

export type ConflictAction = 'skip' | 'overwrite' | 'rename';

interface ConflictDialogProps {
  open: boolean;
  fileName: string;
  title: string;
  description: string;
  skipText: string;
  overwriteText: string;
  renameText: string;
  renamePlaceholder?: string;
  confirmRenameText?: string;
  cancelText?: string;
  onResolve: (action: ConflictAction, newName?: string) => void;
}

export function ConflictDialog({
  open,
  fileName,
  title,
  description,
  skipText,
  overwriteText,
  renameText,
  renamePlaceholder = 'New file name',
  confirmRenameText = 'Confirm Rename',
  cancelText = 'Cancel',
  onResolve,
}: ConflictDialogProps) {
  const [isRenaming, setIsRenaming] = useState(false);
  const [newName, setNewName] = useState('');

  if (!open) return null;

  const handleRenameClick = () => {
    setIsRenaming(true);
    const parts = fileName.split('.');
    if (parts.length > 1) {
      const ext = parts.pop();
      setNewName(`${parts.join('.')}_1.${ext}`);
    } else {
      setNewName(`${fileName}_1`);
    }
  };

  const handleConfirmRename = () => {
    if (newName.trim() && newName.trim() !== fileName) {
      onResolve('rename', newName.trim());
      setIsRenaming(false);
      setNewName('');
    }
  };

  const handleCancelRename = () => {
    setIsRenaming(false);
    setNewName('');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in">
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={() => !isRenaming && onResolve('skip')}
      />
      <div className="relative w-full max-w-sm rounded-xl bg-white p-5 shadow-2xl animate-scale-in sm:p-6">
        <h3 className="mb-2 text-lg font-semibold text-gray-900 sm:text-xl">{title}</h3>
        <p className="mb-5 text-sm text-gray-600 sm:text-base">
          {description.replace('{name}', fileName)}
        </p>

        {isRenaming ? (
          <div className="space-y-4">
            <Input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder={renamePlaceholder}
              autoFocus
              className="min-h-[44px]"
            />
            <div className="flex flex-col gap-2 sm:flex-row sm:gap-3">
              <Button
                variant="outline"
                className="btn-interactive min-h-[44px] flex-1"
                onClick={handleCancelRename}
              >
                {cancelText}
              </Button>
              <Button
                className="btn-interactive min-h-[44px] flex-1"
                onClick={handleConfirmRename}
                disabled={!newName.trim() || newName.trim() === fileName}
              >
                {confirmRenameText}
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-2 sm:flex-row sm:gap-3">
            <Button
              variant="outline"
              className="btn-interactive min-h-[44px] flex-1"
              onClick={() => onResolve('skip')}
            >
              {skipText}
            </Button>
            <Button
              variant="outline"
              className="btn-interactive min-h-[44px] flex-1"
              onClick={handleRenameClick}
            >
              {renameText}
            </Button>
            <Button
              className="btn-interactive min-h-[44px] flex-1"
              onClick={() => onResolve('overwrite')}
            >
              {overwriteText}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
