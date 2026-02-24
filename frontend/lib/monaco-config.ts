import type { Monaco } from '@monaco-editor/react';
import type { editor, Position } from 'monaco-editor';

const SNIPPET_KIND = 27;
const INSERT_AS_SNIPPET = 4;

export const MARKDOWN_SNIPPETS = [
  {
    label: '# Heading 1',
    kind: SNIPPET_KIND,
    insertText: '# ${1:Heading}',
    insertTextRules: INSERT_AS_SNIPPET,
  },
  {
    label: '## Heading 2',
    kind: SNIPPET_KIND,
    insertText: '## ${1:Heading}',
    insertTextRules: INSERT_AS_SNIPPET,
  },
  {
    label: '### Heading 3',
    kind: SNIPPET_KIND,
    insertText: '### ${1:Heading}',
    insertTextRules: INSERT_AS_SNIPPET,
  },
  {
    label: 'Bold',
    kind: SNIPPET_KIND,
    insertText: '**${1:text}**',
    insertTextRules: INSERT_AS_SNIPPET,
  },
  {
    label: 'Italic',
    kind: SNIPPET_KIND,
    insertText: '*${1:text}*',
    insertTextRules: INSERT_AS_SNIPPET,
  },
  {
    label: 'Link',
    kind: SNIPPET_KIND,
    insertText: '[${1:text}](${2:url})',
    insertTextRules: INSERT_AS_SNIPPET,
  },
  {
    label: 'Image',
    kind: SNIPPET_KIND,
    insertText: '![${1:alt}](${2:url})',
    insertTextRules: INSERT_AS_SNIPPET,
  },
  {
    label: 'Code Block',
    kind: SNIPPET_KIND,
    insertText: '```${1:language}\n${2:code}\n```',
    insertTextRules: INSERT_AS_SNIPPET,
  },
  {
    label: 'Inline Code',
    kind: SNIPPET_KIND,
    insertText: '`${1:code}`',
    insertTextRules: INSERT_AS_SNIPPET,
  },
  {
    label: 'Bullet List',
    kind: SNIPPET_KIND,
    insertText: '- ${1:item}\n- ${2:item}',
    insertTextRules: INSERT_AS_SNIPPET,
  },
  {
    label: 'Numbered List',
    kind: SNIPPET_KIND,
    insertText: '1. ${1:item}\n2. ${2:item}',
    insertTextRules: INSERT_AS_SNIPPET,
  },
  {
    label: 'Quote',
    kind: SNIPPET_KIND,
    insertText: '> ${1:quote}',
    insertTextRules: INSERT_AS_SNIPPET,
  },
  {
    label: 'Horizontal Rule',
    kind: SNIPPET_KIND,
    insertText: '---',
  },
  {
    label: 'Table',
    kind: SNIPPET_KIND,
    insertText: '| ${1:Header} | ${2:Header} |\n| --- | --- |\n| ${3:Cell} | ${4:Cell} |',
    insertTextRules: INSERT_AS_SNIPPET,
  },
  {
    label: 'Checkbox',
    kind: SNIPPET_KIND,
    insertText: '- [ ] ${1:task}',
    insertTextRules: INSERT_AS_SNIPPET,
  },
  {
    label: 'Checked Checkbox',
    kind: SNIPPET_KIND,
    insertText: '- [x] ${1:task}',
    insertTextRules: INSERT_AS_SNIPPET,
  },
];

export const MARKDOWN_THEME = {
  base: 'vs',
  inherit: true,
  rules: [],
  colors: {
    'editor.background': '#fafafa',
    'editor.lineHighlightBackground': '#f4f4f5',
    'editorLineNumber.foreground': '#a1a1aa',
    'editorLineNumber.activeForeground': '#71717a',
  },
} as const;

export function configureMonaco(monaco: Monaco): void {
  if (!monaco) return;

  monaco.languages.registerCompletionItemProvider('markdown', {
    provideCompletionItems: (model: editor.ITextModel, position: Position) => {
      const word = model.getWordUntilPosition(position);
      const range = {
        startLineNumber: position.lineNumber,
        endLineNumber: position.lineNumber,
        startColumn: word.startColumn,
        endColumn: word.endColumn,
      };

      const suggestions = MARKDOWN_SNIPPETS.map((snippet) => ({
        ...snippet,
        range,
      }));

      return { suggestions };
    },
  });

  monaco.editor.defineTheme('markdown-light', MARKDOWN_THEME);
}
