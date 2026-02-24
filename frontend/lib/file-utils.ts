export type FileType = 'image' | 'pdf' | 'text' | 'markdown';

const IMAGE_EXTENSIONS: readonly string[] = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
const PDF_EXTENSIONS: readonly string[] = ['pdf'];
const MARKDOWN_EXTENSIONS: readonly string[] = ['md', 'markdown', 'mdx'];

export function getFileType(fileName: string): FileType {
  const ext = fileName.toLowerCase().split('.').pop() || '';

  if (IMAGE_EXTENSIONS.includes(ext)) {
    return 'image';
  }

  if (PDF_EXTENSIONS.includes(ext)) {
    return 'pdf';
  }

  if (MARKDOWN_EXTENSIONS.includes(ext)) {
    return 'markdown';
  }

  return 'text';
}

export function isMarkdown(fileName: string): boolean {
  const ext = fileName.toLowerCase().split('.').pop() || '';
  return MARKDOWN_EXTENSIONS.includes(ext);
}
