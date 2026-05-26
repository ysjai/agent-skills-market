import { describe, test, expect, mock } from "bun:test";
import type { Monaco } from "@monaco-editor/react";
import type { editor, Position } from "monaco-editor";

import {
  MARKDOWN_SNIPPETS,
  MARKDOWN_THEME,
  configureMonaco,
} from "../monaco-config";

describe("MARKDOWN_SNIPPETS", () => {
  test("should contain all 16 snippets", () => {
    expect(MARKDOWN_SNIPPETS).toHaveLength(16);
  });

  test("should have correct Heading 1 snippet", () => {
    const snippet = MARKDOWN_SNIPPETS.find((s) => s.label === "# Heading 1");
    expect(snippet).toBeDefined();
    expect(snippet?.kind).toBe(27);
    expect(snippet?.insertText).toBe("# ${1:Heading}");
    expect(snippet?.insertTextRules).toBe(4);
  });

  test("should have correct Heading 2 snippet", () => {
    const snippet = MARKDOWN_SNIPPETS.find((s) => s.label === "## Heading 2");
    expect(snippet).toBeDefined();
    expect(snippet?.kind).toBe(27);
    expect(snippet?.insertText).toBe("## ${1:Heading}");
    expect(snippet?.insertTextRules).toBe(4);
  });

  test("should have correct Heading 3 snippet", () => {
    const snippet = MARKDOWN_SNIPPETS.find((s) => s.label === "### Heading 3");
    expect(snippet).toBeDefined();
    expect(snippet?.kind).toBe(27);
    expect(snippet?.insertText).toBe("### ${1:Heading}");
    expect(snippet?.insertTextRules).toBe(4);
  });

  test("should have correct Bold snippet", () => {
    const snippet = MARKDOWN_SNIPPETS.find((s) => s.label === "Bold");
    expect(snippet).toBeDefined();
    expect(snippet?.kind).toBe(27);
    expect(snippet?.insertText).toBe("**${1:text}**");
    expect(snippet?.insertTextRules).toBe(4);
  });

  test("should have correct Italic snippet", () => {
    const snippet = MARKDOWN_SNIPPETS.find((s) => s.label === "Italic");
    expect(snippet).toBeDefined();
    expect(snippet?.kind).toBe(27);
    expect(snippet?.insertText).toBe("*${1:text}*");
    expect(snippet?.insertTextRules).toBe(4);
  });

  test("should have correct Link snippet", () => {
    const snippet = MARKDOWN_SNIPPETS.find((s) => s.label === "Link");
    expect(snippet).toBeDefined();
    expect(snippet?.kind).toBe(27);
    expect(snippet?.insertText).toBe("[${1:text}](${2:url})");
    expect(snippet?.insertTextRules).toBe(4);
  });

  test("should have correct Image snippet", () => {
    const snippet = MARKDOWN_SNIPPETS.find((s) => s.label === "Image");
    expect(snippet).toBeDefined();
    expect(snippet?.kind).toBe(27);
    expect(snippet?.insertText).toBe("![${1:alt}](${2:url})");
    expect(snippet?.insertTextRules).toBe(4);
  });

  test("should have correct Code Block snippet", () => {
    const snippet = MARKDOWN_SNIPPETS.find((s) => s.label === "Code Block");
    expect(snippet).toBeDefined();
    expect(snippet?.kind).toBe(27);
    expect(snippet?.insertText).toBe("```${1:language}\n${2:code}\n```");
    expect(snippet?.insertTextRules).toBe(4);
  });

  test("should have correct Inline Code snippet", () => {
    const snippet = MARKDOWN_SNIPPETS.find((s) => s.label === "Inline Code");
    expect(snippet).toBeDefined();
    expect(snippet?.kind).toBe(27);
    expect(snippet?.insertText).toBe("`${1:code}`");
    expect(snippet?.insertTextRules).toBe(4);
  });

  test("should have correct Bullet List snippet", () => {
    const snippet = MARKDOWN_SNIPPETS.find((s) => s.label === "Bullet List");
    expect(snippet).toBeDefined();
    expect(snippet?.kind).toBe(27);
    expect(snippet?.insertText).toBe("- ${1:item}\n- ${2:item}");
    expect(snippet?.insertTextRules).toBe(4);
  });

  test("should have correct Numbered List snippet", () => {
    const snippet = MARKDOWN_SNIPPETS.find((s) => s.label === "Numbered List");
    expect(snippet).toBeDefined();
    expect(snippet?.kind).toBe(27);
    expect(snippet?.insertText).toBe("1. ${1:item}\n2. ${2:item}");
    expect(snippet?.insertTextRules).toBe(4);
  });

  test("should have correct Quote snippet", () => {
    const snippet = MARKDOWN_SNIPPETS.find((s) => s.label === "Quote");
    expect(snippet).toBeDefined();
    expect(snippet?.kind).toBe(27);
    expect(snippet?.insertText).toBe("> ${1:quote}");
    expect(snippet?.insertTextRules).toBe(4);
  });

  test("should have correct Horizontal Rule snippet", () => {
    const snippet = MARKDOWN_SNIPPETS.find(
      (s) => s.label === "Horizontal Rule"
    );
    expect(snippet).toBeDefined();
    expect(snippet?.kind).toBe(27);
    expect(snippet?.insertText).toBe("---");
    expect(snippet?.insertTextRules).toBeUndefined();
  });

  test("should have correct Table snippet", () => {
    const snippet = MARKDOWN_SNIPPETS.find((s) => s.label === "Table");
    expect(snippet).toBeDefined();
    expect(snippet?.kind).toBe(27);
    expect(snippet?.insertText).toBe(
      "| ${1:Header} | ${2:Header} |\n| --- | --- |\n| ${3:Cell} | ${4:Cell} |"
    );
    expect(snippet?.insertTextRules).toBe(4);
  });

  test("should have correct Checkbox snippet", () => {
    const snippet = MARKDOWN_SNIPPETS.find((s) => s.label === "Checkbox");
    expect(snippet).toBeDefined();
    expect(snippet?.kind).toBe(27);
    expect(snippet?.insertText).toBe("- [ ] ${1:task}");
    expect(snippet?.insertTextRules).toBe(4);
  });

  test("should have correct Checked Checkbox snippet", () => {
    const snippet = MARKDOWN_SNIPPETS.find(
      (s) => s.label === "Checked Checkbox"
    );
    expect(snippet).toBeDefined();
    expect(snippet?.kind).toBe(27);
    expect(snippet?.insertText).toBe("- [x] ${1:task}");
    expect(snippet?.insertTextRules).toBe(4);
  });
});

describe("MARKDOWN_THEME", () => {
  test("should have correct base configuration", () => {
    expect(MARKDOWN_THEME.base).toBe("vs");
    expect(MARKDOWN_THEME.inherit).toBe(true);
    expect(MARKDOWN_THEME.rules).toEqual([]);
  });

  test("should have correct color values", () => {
    expect(MARKDOWN_THEME.colors["editor.background"]).toBe("#fafafa");
    expect(MARKDOWN_THEME.colors["editor.lineHighlightBackground"]).toBe(
      "#f4f4f5"
    );
    expect(MARKDOWN_THEME.colors["editorLineNumber.foreground"]).toBe(
      "#a1a1aa"
    );
    expect(MARKDOWN_THEME.colors["editorLineNumber.activeForeground"]).toBe(
      "#71717a"
    );
  });
});

describe("configureMonaco", () => {
  const createMockMonaco = () => {
    const registerCompletionItemProvider = mock(
      (language: string, provider: unknown) => provider
    );
    const defineTheme = mock((_name: string, _theme: unknown) => undefined);

    return {
      languages: {
        registerCompletionItemProvider,
      },
      editor: {
        defineTheme,
      },
      _getProvider: () => registerCompletionItemProvider.mock.calls[0]?.[1],
      _getThemeCall: () => defineTheme.mock.calls[0],
    };
  };

  test("should return early when monaco is null", () => {
    configureMonaco(null as unknown as Monaco);
    // Should not throw and should return early
    expect(true).toBe(true);
  });

  test("should return early when monaco is undefined", () => {
    configureMonaco(undefined as unknown as Monaco);
    // Should not throw and should return early
    expect(true).toBe(true);
  });

  test("should register completion item provider for markdown", () => {
    const mockMonaco = createMockMonaco();
    configureMonaco(mockMonaco as unknown as Monaco);

    expect(mockMonaco.languages.registerCompletionItemProvider).toHaveBeenCalled();
    const calls = mockMonaco.languages.registerCompletionItemProvider.mock.calls;
    expect(calls[0][0]).toBe("markdown");
    expect(calls[0][1]).toHaveProperty("provideCompletionItems");
  });

  test("should define markdown-light theme", () => {
    const mockMonaco = createMockMonaco();
    configureMonaco(mockMonaco as unknown as Monaco);

    expect(mockMonaco.editor.defineTheme).toHaveBeenCalled();
    const themeCall = mockMonaco._getThemeCall();
    expect(themeCall[0]).toBe("markdown-light");
    expect(themeCall[1]).toBe(MARKDOWN_THEME);
  });

  test("should return correct suggestions with range from provider", () => {
    const mockMonaco = createMockMonaco();
    configureMonaco(mockMonaco as unknown as Monaco);

    const provider = mockMonaco._getProvider();
    expect(provider).toBeDefined();

    const mockModel = {
      getWordUntilPosition: mock(() => ({
        startColumn: 5,
        endColumn: 10,
      })),
    } as unknown as editor.ITextModel;

    const mockPosition = {
      lineNumber: 3,
      column: 8,
    } as Position;

    const result = provider.provideCompletionItems(mockModel, mockPosition);

    expect(result).toHaveProperty("suggestions");
    expect(result.suggestions).toHaveLength(16);

    // Verify each suggestion has the correct range
    result.suggestions.forEach((suggestion: typeof MARKDOWN_SNIPPETS[0] & { range: unknown }) => {
      expect(suggestion.range).toEqual({
        startLineNumber: 3,
        endLineNumber: 3,
        startColumn: 5,
        endColumn: 10,
      });
    });

    // Verify first suggestion has correct properties
    expect(result.suggestions[0]).toMatchObject({
      label: "# Heading 1",
      kind: 27,
      insertText: "# ${1:Heading}",
      insertTextRules: 4,
    });

    // Verify Horizontal Rule snippet (no insertTextRules)
    const horizontalRule = result.suggestions.find(
      (s: typeof MARKDOWN_SNIPPETS[0] & { range: unknown }) => s.label === "Horizontal Rule"
    );
    expect(horizontalRule?.insertTextRules).toBeUndefined();
    expect(horizontalRule?.insertText).toBe("---");
  });

  test("should call getWordUntilPosition with correct position", () => {
    const mockMonaco = createMockMonaco();
    configureMonaco(mockMonaco as unknown as Monaco);

    const provider = mockMonaco._getProvider();

    const mockGetWordUntilPosition = mock(() => ({
      startColumn: 1,
      endColumn: 5,
    }));

    const mockModel = {
      getWordUntilPosition: mockGetWordUntilPosition,
    } as unknown as editor.ITextModel;

    const mockPosition = {
      lineNumber: 10,
      column: 15,
    } as Position;

    provider.provideCompletionItems(mockModel, mockPosition);

    expect(mockGetWordUntilPosition).toHaveBeenCalledWith(mockPosition);
  });
});
