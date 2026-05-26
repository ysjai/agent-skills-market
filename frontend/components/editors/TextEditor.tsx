'use client';

import React, { useEffect, useImperativeHandle, useRef, useState } from 'react';
import Editor, { type OnMount } from '@monaco-editor/react';
import type { editor } from 'monaco-editor';
import { Loader2, Save, AlertCircle, Download } from 'lucide-react';

import { api } from '@/lib/api';
import { getFileIcon } from '@/components/ui/FileIcons';
import { getErrorMessage, isAbortError } from '@/lib/errors';
import { logger } from '@/lib/logger';
import { cn } from '@/lib/utils';
import { configureMonaco, MARKDOWN_EDITOR_OPTIONS } from '@/lib/monaco-config';

interface TextEditorProps {
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

export interface TextEditorRef {
  isModified: boolean;
  resetModified: () => void;
  resetContent: () => void;
}

type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

export const TextEditor = React.forwardRef<TextEditorRef, TextEditorProps>(({
  blobId,
  treeId,
  filePath,
  initialContent = '',
  fileName = 'untitled.md',
  onSave,
  onChange,
  onDownload,
  className,
  height = '500px',
  readOnly = false,
}, ref) => {
  const [content, setContent] = useState(initialContent);
  const [originalContent, setOriginalContent] = useState(initialContent);
  const [isModified, setIsModified] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [error, setError] = useState<string | null>(null);
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  useImperativeHandle(ref, () => ({
    isModified,
    resetModified: () => {
      setIsModified(false);
    },
    resetContent: () => {
      setContent(originalContent);
      setIsModified(false);
      setSaveStatus('idle');
    },
  }), [isModified, originalContent]);

  useEffect(() => {
    if (blobId) {
      setSaveStatus('idle');
      loadBlobContent(blobId);
    }

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
        abortControllerRef.current = null;
      }
    };
  }, [blobId]);

  const loadBlobContent = async (id: string) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;

    setIsLoading(true);
    setError(null);
    try {
      const response = await api.getBlob(`/blobs/${id}`, {
        signal: controller.signal,
      });
      const text = await response.text();
      setContent(text);
      setOriginalContent(text);
    } catch (err) {
      if (isAbortError(err)) {
        return;
      }

      const errorMessage = getErrorMessage(err, 'Failed to load file content');
      setError(errorMessage);
      logger.error('Error loading blob:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const saveBlobContent = async (newContent: string) => {
    // If we have treeId and filePath, use the tree update API
    if (treeId && filePath) {
      setSaveStatus('saving');
      try {
        const response = await api.put<{
          id: string;
          entries: Array<{
            path: string;
            blob_id: string | null;
            type: string;
          }>;
          created_at: string;
        }>(`/trees/${treeId}/files/content`, {
          path: filePath,
          content: newContent,
        });

        const updatedEntry = response.entries.find(
          (entry) => entry.path === filePath
        );
        const newBlobId = updatedEntry?.blob_id;

        setSaveStatus('saved');
        setIsModified(false);
        setOriginalContent(newContent);
        if (filePath) {
          onSave?.(newContent, filePath, newBlobId || undefined);
        }
      } catch (err) {
        setSaveStatus('error');
        const errorMessage = getErrorMessage(err, 'Failed to save file');
        setError(errorMessage);
        logger.error('Error saving blob:', err);
      }
      return;
    }

    // Fallback: If no blobId, just call onSave callback
    if (!blobId) {
      if (filePath) {
        onSave?.(newContent, filePath);
      }
      setSaveStatus('saved');
      setIsModified(false);
      setOriginalContent(newContent);
      return;
    }

    setSaveStatus('saving');
    try {
      // Create a Blob from the content
      const blob = new Blob([newContent], { type: 'text/markdown' });
      const formData = new FormData();
      formData.append('file', blob, fileName);

      // Upload the blob
      await api.put(`/blobs/${blobId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setSaveStatus('saved');
      setIsModified(false);
      setOriginalContent(newContent);
      if (filePath) {
        onSave?.(newContent, filePath);
      }
    } catch (err) {
      setSaveStatus('error');
      const errorMessage = getErrorMessage(err, 'Failed to save file');
      setError(errorMessage);
      logger.error('Error saving blob:', err);
    }
  };

  const handleEditorChange = (value: string | undefined) => {
    const newContent = value || '';
    setContent(newContent);
    setSaveStatus('idle');
    onChange?.(newContent);
    setIsModified(newContent !== originalContent);
  };

  const handleEditorDidMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;

    // Configure Monaco instance
    configureMonaco(monaco);

    // Add keyboard shortcuts
    if (monaco) {
      editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
        saveBlobContent(content);
      });
    }
  };

  const renderSaveStatus = () => {
    switch (saveStatus) {
      case 'saving':
        return (
          <span className="flex items-center gap-1.5 text-sm text-gray-500">
            <Loader2 className="w-4 h-4 animate-spin" />
            Saving...
          </span>
        );
      case 'error':
        return (
          <span className="flex items-center gap-1.5 text-sm text-red-600">
            <AlertCircle className="w-4 h-4" />
            Save failed
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className={cn('flex flex-col border border-gray-200 rounded-lg overflow-hidden bg-white', className)}>
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center gap-2">
          {getFileIcon(fileName, filePath)}
          <span className="text-sm font-medium text-gray-700">{fileName}</span>
        </div>
        <div className="flex items-center gap-3">
          {renderSaveStatus()}
          <div className="flex items-center gap-1">
            <button
              onClick={() => saveBlobContent(content)}
              disabled={saveStatus === 'saving' || readOnly || !isModified}
              className={cn(
                'flex items-center justify-center w-8 h-8 rounded-md transition-colors',
                saveStatus === 'saving' || readOnly || !isModified
                  ? 'text-gray-400 cursor-not-allowed'
                  : 'text-gray-700 hover:bg-gray-200 active:scale-95'
              )}
              title="Save File"
            >
              {saveStatus === 'saving' ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Save className="w-4 h-4" />
              )}
            </button>
            {onDownload && (
              <button
                onClick={onDownload}
                disabled={saveStatus === 'saving'}
                className="flex items-center justify-center w-8 h-8 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded-md transition-colors"
                title="Download File"
              >
                <Download className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 px-4 py-2 bg-red-50 border-b border-red-100">
          <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
          <span className="text-sm text-red-700">{error}</span>
        </div>
      )}

      <div className="relative">
        {isLoading ? (
          <div className="flex items-center justify-center" style={{ height }}>
            <div className="flex items-center gap-2 text-gray-500">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span className="text-sm">Loading...</span>
            </div>
          </div>
        ) : (
          <Editor
            height={height}
            language="markdown"
            value={content}
            theme="markdown-light"
            onChange={handleEditorChange}
            onMount={handleEditorDidMount}
            options={MARKDOWN_EDITOR_OPTIONS(readOnly)}
            loading={
              <div className="flex items-center justify-center" style={{ height }}>
                <div className="flex items-center gap-2 text-gray-500">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span className="text-sm">Initializing editor...</span>
                </div>
              </div>
            }
          />
        )}
      </div>

      <div className="flex items-center justify-between px-4 py-2 border-t border-gray-200 bg-gray-50 text-xs text-gray-500">
        <div className="flex items-center gap-4">
          <span>Markdown</span>
          <span>{content.split('\n').length} lines</span>
          <span>{content.length} characters</span>
        </div>
        <div className="flex items-center gap-3">
          <span>Ctrl+S to save</span>
          <span>Ctrl+Space for suggestions</span>
        </div>
      </div>
    </div>
  );
});

TextEditor.displayName = 'TextEditor';

export default TextEditor;
