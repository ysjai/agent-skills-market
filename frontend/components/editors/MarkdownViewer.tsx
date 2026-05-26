'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import Editor from '@monaco-editor/react';
import { Loader2, Eye, FileCode, Copy, Check, Download, ExternalLink } from 'lucide-react';

import { api } from '@/lib/api';
import { getFileIcon } from '@/components/ui/FileIcons';
import { getErrorMessage } from '@/lib/errors';
import { useClipboard } from '@/hooks/useClipboard';
import { MARKDOWN_TYPOGRAPHY_STYLES } from '@/lib/markdown-styles';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';

interface FrontmatterMetadata {
  name?: string;
  description?: string;
  [key: string]: string | undefined;
}

function parseFrontmatter(content: string): { metadata: FrontmatterMetadata; body: string } {
  const frontmatterMatch = content.match(/^---\s*\n([\s\S]*?)\n---/);
  if (!frontmatterMatch) {
    return { metadata: {}, body: content };
  }

  const frontmatter = frontmatterMatch[1];
  const body = content.slice(frontmatterMatch[0].length).trimStart();
  const metadata: FrontmatterMetadata = {};

  const lines = frontmatter.split('\n');
  for (const line of lines) {
    const match = line.match(/^([\w-]+):\s*(.+)$/);
    if (match) {
      const key = match[1].trim();
      const value = match[2].trim();
      metadata[key] = value;
    }
  }

  return { metadata, body };
}

function MetadataCard({
  metadata,
}: {
  metadata: FrontmatterMetadata;
}) {
  const entries = Object.entries(metadata);
  if (entries.length === 0) {
    return null;
  }

  return (
    <div className="mb-5 space-y-1 rounded-md bg-gray-50 p-4">
      {entries.map(([key, value]) => (
        <div key={key} className="flex items-baseline gap-2 text-sm">
          <span className="shrink-0 text-base font-semibold text-gray-900">{key}:</span>
          <span className="text-sm text-gray-600">{value}</span>
        </div>
      ))}
    </div>
  );
}

interface MarkdownViewerProps {
  blobId?: string;
  treeId?: string;
  filePath?: string;
  initialContent?: string;
  fileName?: string;
  onDownload?: () => void;
  className?: string;
  height?: string;
  blobUrl?: string;
}

type ViewMode = 'preview' | 'source';

export function MarkdownViewer({
  blobId,
  filePath,
  initialContent = '',
  fileName = 'untitled.md',
  onDownload,
  className,
  height = '500px',
  blobUrl,
}: MarkdownViewerProps) {
  const [rawContent, setRawContent] = useState(initialContent);
  const [viewMode, setViewMode] = useState<ViewMode>('preview');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { copy, copied } = useClipboard();
  const t = useTranslations('fileViewer');
  const tCommon = useTranslations('common');

  const { metadata, body } = parseFrontmatter(rawContent);
  const displayContent = Object.keys(metadata).length > 0 ? body : rawContent;

  const loadBlobContent = useCallback(async (id: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const url = blobUrl || `/blobs/${id}`;
      const response = await api.getBlob(url);
      const text = await response.text();
      setRawContent(text);
    } catch (err) {
      const errorMessage = getErrorMessage(err, 'Failed to load file content');
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [blobUrl]);

  useEffect(() => {
    if (blobId) {
      void loadBlobContent(blobId);
    }
  }, [blobId, loadBlobContent]);

  const handleCopy = () => {
    copy(rawContent);
  };

  const components = {
    a: ({ href, children, ...props }: React.AnchorHTMLAttributes<HTMLAnchorElement>) => (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-0.5 text-indigo-600 hover:text-indigo-800 underline underline-offset-2 transition-colors"
        {...props}
      >
        {children}
        <ExternalLink className="w-3 h-3 ml-0.5 opacity-60" />
      </a>
    ),
    h2: ({ children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => (
      <h2
        className="text-xl font-semibold text-gray-800 mt-8 mb-4"
        {...props}
      >
        {children}
      </h2>
    ),
    pre: ({ children }: React.HTMLAttributes<HTMLPreElement>) => (
      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto my-4 text-sm leading-relaxed shadow-inner [&_code]:!bg-transparent [&_code]:!text-inherit [&_code]:!border-0 [&_code]:!p-0 [&_code]:!rounded-none">
        {children}
      </pre>
    ),
    code: ({ children }: React.HTMLAttributes<HTMLElement>) => (
      <code className="bg-gray-100 text-indigo-600 px-1.5 py-0.5 rounded text-sm font-mono border border-gray-200">
        {children}
      </code>
    ),
  };

  return (
    <div className={cn('flex flex-col border border-gray-200 rounded-lg overflow-hidden bg-white', className)}>
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center gap-2">
          {getFileIcon(fileName, filePath)}
          <span className="text-sm font-medium text-gray-700">{fileName}</span>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center bg-gray-100 rounded-lg p-0.5">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setViewMode('preview')}
              className={cn(
                'h-7 px-2.5 text-xs font-medium rounded-md transition-all',
                viewMode === 'preview'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200'
              )}
            >
              <Eye className="w-3.5 h-3.5 mr-1.5" />
              {t('preview')}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setViewMode('source')}
              className={cn(
                'h-7 px-2.5 text-xs font-medium rounded-md transition-all',
                viewMode === 'source'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200'
              )}
            >
              <FileCode className="w-3.5 h-3.5 mr-1.5" />
              {t('source')}
            </Button>
          </div>

          <div className="w-px h-5 bg-gray-300 mx-1" />

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
        ) : viewMode === 'preview' ? (
          <div
            className={cn("max-w-none p-6 overflow-auto", MARKDOWN_TYPOGRAPHY_STYLES)}
            style={{ height }}
          >
            {Object.keys(metadata).length > 0 && <MetadataCard metadata={metadata} />}
            <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
              {displayContent}
            </ReactMarkdown>
          </div>
        ) : (
          <Editor
            height={height}
            language="markdown"
            value={rawContent}
            theme="markdown-light"
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
          <span>Markdown</span>
          <span>{rawContent.split('\n').length} lines</span>
          <span>{rawContent.length} characters</span>
        </div>
        <div>
          <span>{t('readOnly')}</span>
        </div>
      </div>
    </div>
  );
}

export default MarkdownViewer;
