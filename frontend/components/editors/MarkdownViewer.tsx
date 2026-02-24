'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import Editor from '@monaco-editor/react';
import { api } from '@/lib/api';
import { getFileIcon } from '@/components/ui/FileIcons';
import { getErrorMessage } from '@/lib/errors';
import { useClipboard } from '@/hooks/useClipboard';
import { cn } from '@/lib/utils';
import { Loader2, Eye, FileCode, Copy, Check, Download, ExternalLink } from 'lucide-react';
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

const typographyStylesForMarkdown = `
  [&>h1]:text-3xl [&>h1]:font-bold [&>h1]:text-gray-900 [&>h1]:mb-6 [&>h1]:pb-3 [&>h1]:border-b [&>h1]:border-gray-200
  [&>h2]:text-xl [&>h2]:font-semibold [&>h2]:text-gray-800 [&>h2]:mt-8 [&>h2]:mb-4 [&>h2]:flex [&>h2]:items-center [&>h2]:gap-2
  [&>h3]:text-lg [&>h3]:font-semibold [&>h3]:text-gray-800 [&>h3]:mt-6 [&>h3]:mb-3
  [&>h4]:text-base [&>h4]:font-semibold [&>h4]:text-gray-800 [&>h4]:mt-5 [&>h4]:mb-2
  [&>p]:text-gray-700 [&>p]:leading-relaxed [&>p]:mb-4 [&>p]:text-[15px]
  [&>p>strong]:text-gray-900 [&>p>strong]:font-semibold
  [&>ul]:list-disc [&>ul]:pl-6 [&>ul]:mb-4 [&>ul]:space-y-2
  [&>ol]:list-decimal [&>ol]:pl-6 [&>ol]:mb-4 [&>ol]:space-y-2
  [&>ul>li]:text-gray-700 [&>ul>li]:leading-relaxed [&>ul>li]:text-[15px]
  [&>ol>li]:text-gray-700 [&>ol>li]:leading-relaxed [&>ol>li]:text-[15px]
  [&>ul>li>strong]:text-gray-900 [&>ul>li>strong]:font-semibold
  [&>ol>li>strong]:text-gray-900 [&>ol>li>strong]:font-semibold
  [&>blockquote]:border-l-4 [&>blockquote]:border-indigo-400 [&>blockquote]:pl-4 [&>blockquote]:py-1 [&>blockquote]:my-6 [&>blockquote]:bg-indigo-50/50 [&>blockquote]:italic [&>blockquote]:text-gray-700 [&>blockquote]:rounded-r-md
  [&>pre]:bg-gray-900 [&>pre]:text-gray-100 [&>pre]:p-4 [&>pre]:rounded-lg [&>pre]:overflow-x-auto [&>pre]:my-4 [&>pre]:text-sm [&>pre]:leading-relaxed [&>pre]:font-mono [&>pre]:shadow-inner
  [&>p>code]:bg-gray-100 [&>p>code]:text-indigo-600 [&>p>code]:px-1.5 [&>p>code]:py-0.5 [&>p>code]:rounded [&>p>code]:text-sm [&>p>code]:font-mono [&>p>code]:border [&>p>code]:border-gray-200
  [&>ul>li>code]:bg-gray-100 [&>ul>li>code]:text-indigo-600 [&>ul>li>code]:px-1.5 [&>ul>li>code]:py-0.5 [&>ul>li>code]:rounded [&>ul>li>code]:text-sm [&>ul>li>code]:font-mono
  [&>a]:text-indigo-600 [&>a]:underline [&>a]:underline-offset-2 [&>a]:hover:text-indigo-800 [&>a]:transition-colors
  [&>hr]:border-gray-200 [&>hr]:my-8
  [&>table]:w-full [&>table]:border-collapse [&>table]:my-4 [&>table]:text-sm
  [&>table>thead>tr]:border-b [&>table>thead>tr]:border-gray-300
  [&>table>thead>tr>th]:py-2 [&>table>thead>tr>th]:px-3 [&>table>thead>tr>th]:text-left [&>table>thead>tr>th]:font-semibold [&>table>thead>tr>th]:text-gray-700
  [&>table>tbody>tr]:border-b [&>table>tbody>tr]:border-gray-100 [&>table>tbody>tr:last-child]:border-0
  [&>table>tbody>tr>td]:py-2 [&>table>tbody>tr>td]:px-3 [&>table>tbody>tr>td]:text-gray-600
`;

interface MarkdownViewerProps {
  blobId?: string;
  treeId?: string;
  filePath?: string;
  initialContent?: string;
  fileName?: string;
  onDownload?: () => void;
  className?: string;
  height?: string;
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
      setRawContent(text);
    } catch (err) {
      const errorMessage = getErrorMessage(err, 'Failed to load file content');
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

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
            className={cn("max-w-none p-6 overflow-auto", typographyStylesForMarkdown)}
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
