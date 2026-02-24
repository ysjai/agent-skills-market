'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import Editor from '@monaco-editor/react';
import { api } from '@/lib/api';
import { getFileIcon } from '@/components/ui/FileIcons';
import { getErrorMessage } from '@/lib/errors';
import { useClipboard } from '@/hooks/useClipboard';
import { cn } from '@/lib/utils';
import { Loader2, Copy, Check, Download } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface TextViewerProps {
  blobId?: string;
  filePath?: string;
  initialContent?: string;
  fileName?: string;
  onDownload?: () => void;
  className?: string;
  height?: string;
}

export function TextViewer({
  blobId,
  filePath,
  initialContent = '',
  fileName = 'untitled.txt',
  onDownload,
  className,
  height = '500px',
}: TextViewerProps) {
  const [content, setContent] = useState(initialContent);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { copy, copied } = useClipboard();
  const t = useTranslations('fileViewer');
  const tCommon = useTranslations('common');

  useEffect(() => {
    if (blobId) {
      loadBlobContent(blobId);
    }
  }, [blobId]);

  const loadBlobContent = async (id: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.getBlob(`/blobs/${id}`);
      const text = await response.text();
      setContent(text);
    } catch (err) {
      const errorMessage = getErrorMessage(err, 'Failed to load file content');
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = () => {
    copy(content);
  };

  const getLanguage = (fileName: string): string => {
    const ext = fileName.toLowerCase().split('.').pop() || '';
    const languageMap: Record<string, string> = {
      js: 'javascript',
      jsx: 'javascript',
      ts: 'typescript',
      tsx: 'typescript',
      py: 'python',
      json: 'json',
      yaml: 'yaml',
      yml: 'yaml',
      html: 'html',
      css: 'css',
      scss: 'scss',
      sql: 'sql',
      sh: 'shell',
      bash: 'shell',
      zsh: 'shell',
      xml: 'xml',
      toml: 'toml',
      ini: 'ini',
      env: 'plaintext',
      log: 'plaintext',
      txt: 'plaintext',
    };
    return languageMap[ext] || 'plaintext';
  };

  return (
    <div className={cn('flex flex-col border border-gray-200 rounded-lg overflow-hidden bg-white', className)}>
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center gap-2">
          {getFileIcon(fileName, filePath)}
          <span className="text-sm font-medium text-gray-700">{fileName}</span>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={handleCopy}
            className="h-8 w-8 text-gray-600 hover:text-gray-900 hover:bg-gray-200"
            title={t('copy')}
          >
            {copied ? (
              <Check className="w-4 h-4 text-green-600" />
            ) : (
              <Copy className="w-4 h-4" />
            )}
          </Button>

          {onDownload && (
            <Button
              variant="ghost"
              size="icon"
              onClick={onDownload}
              className="h-8 w-8 text-gray-600 hover:text-gray-900 hover:bg-gray-200"
              title={t('download')}
            >
              <Download className="w-4 h-4" />
            </Button>
          )}
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 px-4 py-2 bg-red-50 border-b border-red-100">
          <span className="text-sm text-red-700">{error}</span>
        </div>
      )}

      <div className="relative flex-1 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center" style={{ height }}>
            <div className="flex items-center gap-2 text-gray-500">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span className="text-sm">{tCommon('loading')}</span>
            </div>
          </div>
        ) : (
          <Editor
            height={height}
            language={getLanguage(fileName)}
            value={content}
            theme="light"
            options={{
              readOnly: true,
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              wordWrap: 'on',
              lineNumbers: 'on',
              folding: true,
              renderWhitespace: 'selection',
              automaticLayout: true,
              fontSize: 14,
              fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Monaco, Consolas, monospace',
              lineHeight: 1.6,
              padding: { top: 16, bottom: 16 },
              scrollbar: {
                vertical: 'auto',
                horizontal: 'auto',
              },
            }}
            loading={
              <div className="flex items-center justify-center" style={{ height }}>
                <div className="flex items-center gap-2 text-gray-500">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span className="text-sm">{tCommon('loading')}</span>
                </div>
              </div>
            }
          />
        )}
      </div>

      <div className="flex items-center justify-between px-4 py-2 border-t border-gray-200 bg-gray-50 text-xs text-gray-500">
        <div className="flex items-center gap-4">
          <span>{getLanguage(fileName).toUpperCase()}</span>
          <span>{content.split('\n').length} lines</span>
          <span>{content.length} characters</span>
        </div>
        <div>
          <span>{t('readOnly')}</span>
        </div>
      </div>
    </div>
  );
}

export default TextViewer;
