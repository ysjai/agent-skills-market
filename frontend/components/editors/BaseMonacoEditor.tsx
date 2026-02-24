'use client';

import React from 'react';
import Editor, { type OnMount } from '@monaco-editor/react';
import { Loader2 } from 'lucide-react';

export interface BaseMonacoEditorProps {
  height?: string;
  value: string;
  onChange?: (value: string | undefined) => void;
  onMount?: OnMount;
  readOnly?: boolean;
  loading?: React.ReactNode;
  className?: string;
}

const defaultOptions = {
  minimap: { enabled: false },
  scrollBeyondLastLine: false,
  wordWrap: 'on' as const,
  lineNumbers: 'on' as const,
  folding: true,
  renderWhitespace: 'selection' as const,
  automaticLayout: true,
  fontSize: 14,
  fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Monaco, Consolas, monospace',
  lineHeight: 1.6,
  padding: { top: 16, bottom: 16 },
  scrollbar: {
    vertical: 'auto' as const,
    horizontal: 'auto' as const,
  },
  quickSuggestions: true,
  suggestOnTriggerCharacters: true,
  acceptSuggestionOnCommitCharacter: true,
  autoIndent: 'advanced' as const,
  formatOnPaste: true,
  formatOnType: true,
};

const defaultLoading = (height?: string) => (
  <div className="flex items-center justify-center" style={{ height }}>
    <div className="flex items-center gap-2 text-gray-500">
      <Loader2 className="w-5 h-5 animate-spin" />
      <span className="text-sm">Initializing editor...</span>
    </div>
  </div>
);

export function BaseMonacoEditor({
  height = '500px',
  value,
  onChange,
  onMount,
  readOnly = false,
  loading,
  className,
}: BaseMonacoEditorProps) {
  return (
    <div className={className}>
      <Editor
        height={height}
        language="markdown"
        value={value}
        theme="markdown-light"
        onChange={onChange}
        onMount={onMount}
        options={{
          ...defaultOptions,
          readOnly,
        }}
        loading={loading ?? defaultLoading(height)}
      />
    </div>
  );
}

export default BaseMonacoEditor;
