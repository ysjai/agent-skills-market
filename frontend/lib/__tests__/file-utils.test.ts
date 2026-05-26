import { describe, it, expect } from 'bun:test';

import { getFileType, isMarkdown } from '../file-utils';

describe('getFileType', () => {
  it('根据扩展名正确识别常见文件类型', () => {
    expect(getFileType('photo.jpg')).toBe('image');
    expect(getFileType('photo.jpeg')).toBe('image');
    expect(getFileType('photo.png')).toBe('image');
    expect(getFileType('document.pdf')).toBe('pdf');
    expect(getFileType('readme.txt')).toBe('text');
  });

  it('不区分大小写', () => {
    expect(getFileType('IMAGE.PNG')).toBe('image');
    expect(getFileType('Photo.JPEG')).toBe('image');
    expect(getFileType('DOCUMENT.PDF')).toBe('pdf');
  });

  it('未知扩展名和无扩展名默认为 text', () => {
    expect(getFileType('file.xyz')).toBe('text');
    expect(getFileType('file')).toBe('text');
    expect(getFileType('file.unknown')).toBe('text');
  });

  it('识别 markdown 文件', () => {
    expect(getFileType('readme.md')).toBe('markdown');
    expect(getFileType('doc.markdown')).toBe('markdown');
    expect(getFileType('page.mdx')).toBe('markdown');
  });
});

describe('isMarkdown', () => {
  it('returns true for .md files', () => {
    expect(isMarkdown('readme.md')).toBe(true);
    expect(isMarkdown('document.md')).toBe(true);
  });

  it('returns true for .markdown files', () => {
    expect(isMarkdown('readme.markdown')).toBe(true);
  });

  it('returns true for .mdx files', () => {
    expect(isMarkdown('component.mdx')).toBe(true);
  });

  it('returns false for non-markdown files', () => {
    expect(isMarkdown('file.txt')).toBe(false);
    expect(isMarkdown('file.ts')).toBe(false);
    expect(isMarkdown('file.js')).toBe(false);
    expect(isMarkdown('file.pdf')).toBe(false);
  });

  it('is case insensitive', () => {
    expect(isMarkdown('README.MD')).toBe(true);
    expect(isMarkdown('Doc.Markdown')).toBe(true);
    expect(isMarkdown('Page.MDX')).toBe(true);
  });

  it('returns false for files without extension', () => {
    expect(isMarkdown('README')).toBe(false);
    expect(isMarkdown('file')).toBe(false);
  });
});
