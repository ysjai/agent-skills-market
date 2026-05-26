/* eslint-disable @next/next/no-img-element */

import {
  FileText,
  FileCode,
  File,
  FileType2,
} from 'lucide-react';
import React from 'react';

const JSIcon: React.FC = () => (
  <img src="/file-item-icons/js.svg" alt="JavaScript" className="h-4 w-4" />
);

const PythonIcon: React.FC = () => (
  <img src="/file-item-icons/python.svg" alt="Python" className="h-4 w-4" />
);

const HTMLIcon: React.FC = () => (
  <img src="/file-item-icons/html.svg" alt="HTML" className="h-4 w-4" />
);

const PDFIcon: React.FC = () => (
  <img src="/file-item-icons/pdf.svg" alt="PDF" className="h-4 w-4" />
);

const ImageIcon: React.FC = () => (
  <img src="/file-item-icons/image.svg" alt="Image" className="h-4 w-4" />
);

const CSSIcon: React.FC = () => (
  <img src="/file-item-icons/css.svg" alt="CSS" className="h-4 w-4" />
);

const JavaIcon: React.FC = () => (
  <img src="/file-item-icons/java.svg" alt="Java" className="h-4 w-4" />
);

const JSONIcon: React.FC = () => (
  <img src="/file-item-icons/json.svg" alt="JSON" className="h-4 w-4" />
);

const MDIcon: React.FC = () => (
  <img src="/file-item-icons/md.svg" alt="Markdown" className="h-4 w-4" />
);

const ShellIcon: React.FC = () => (
  <img src="/file-item-icons/shell.svg" alt="Shell" className="h-4 w-4" />
);

const SkillSVGIcon: React.FC = () => (
  <img src="/file-item-icons/skill.svg" alt="Skill" className="h-4 w-4" />
);

export const MarkdownIcon: React.FC<{ className?: string }> = ({ className = 'h-4 w-4' }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M4 16V8l4 4 4-4v8" />
    <path d="M16 8v8l2-2" />
    <path d="M16 16l-2-2" />
  </svg>
);

export const SkillFileIcon: React.FC<{ className?: string }> = ({ className = 'h-4 w-4' }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14,2 14,8 20,8" />
    <path d="M8 16V12l2 2 2-2v4" />
    <path d="M16 12v4" />
    <path d="M15 12h2" />
    <path d="M18 3l.5 1.5L20 5l-1.5.5L18 7l-.5-1.5L16 5l1.5-.5z" fill="currentColor" />
  </svg>
);

const FILE_TYPE_ICONS: Record<string, { icon: React.ReactNode; color: string }> = {
  // JavaScript files use JS icon with background (yellow)
  js: { icon: <JSIcon />, color: 'text-yellow-400' },
  jsx: { icon: <JSIcon />, color: 'text-yellow-400' },
  mjs: { icon: <JSIcon />, color: 'text-yellow-400' },
  cjs: { icon: <JSIcon />, color: 'text-yellow-400' },
  ts: { icon: <FileCode className="h-4 w-4" />, color: 'text-blue-500' },
  tsx: { icon: <FileCode className="h-4 w-4" />, color: 'text-blue-500' },
  // Python files use Py icon with background (blue)
  py: { icon: <PythonIcon />, color: 'text-blue-500' },
  rb: { icon: <FileCode className="h-4 w-4" />, color: 'text-red-500' },
  go: { icon: <FileCode className="h-4 w-4" />, color: 'text-cyan-500' },
  rs: { icon: <FileCode className="h-4 w-4" />, color: 'text-orange-500' },
  java: { icon: <JavaIcon />, color: 'text-red-600' },
  kt: { icon: <FileCode className="h-4 w-4" />, color: 'text-purple-500' },
  swift: { icon: <FileCode className="h-4 w-4" />, color: 'text-orange-500' },
  c: { icon: <FileCode className="h-4 w-4" />, color: 'text-blue-600' },
  cpp: { icon: <FileCode className="h-4 w-4" />, color: 'text-blue-600' },
  h: { icon: <FileCode className="h-4 w-4" />, color: 'text-purple-600' },
  md: { icon: <MDIcon />, color: 'text-slate-700' },
  markdown: { icon: <MDIcon />, color: 'text-slate-700' },
  json: { icon: <JSONIcon />, color: 'text-yellow-600' },
  yaml: { icon: <FileText className="h-4 w-4" />, color: 'text-red-400' },
  yml: { icon: <FileText className="h-4 w-4" />, color: 'text-red-400' },
  xml: { icon: <FileText className="h-4 w-4" />, color: 'text-orange-500' },
  html: { icon: <HTMLIcon />, color: 'text-orange-600' },
  htm: { icon: <HTMLIcon />, color: 'text-orange-600' },
  css: { icon: <CSSIcon />, color: 'text-blue-400' },
  scss: { icon: <CSSIcon />, color: 'text-pink-500' },
  less: { icon: <CSSIcon />, color: 'text-pink-500' },
  txt: { icon: <FileText className="h-4 w-4" />, color: 'text-gray-400' },
  log: { icon: <FileText className="h-4 w-4" />, color: 'text-gray-400' },
  sh: { icon: <ShellIcon />, color: 'text-green-600' },
  bash: { icon: <ShellIcon />, color: 'text-green-600' },
  zsh: { icon: <ShellIcon />, color: 'text-green-600' },
  sql: { icon: <FileCode className="h-4 w-4" />, color: 'text-blue-400' },
  dockerfile: { icon: <FileCode className="h-4 w-4" />, color: 'text-blue-500' },
  env: { icon: <FileCode className="h-4 w-4" />, color: 'text-yellow-600' },
  gitignore: { icon: <FileText className="h-4 w-4" />, color: 'text-gray-400' },
  readme: { icon: <FileType2 className="h-4 w-4" />, color: 'text-blue-600' },
  toml: { icon: <FileText className="h-4 w-4" />, color: 'text-gray-600' },
  ini: { icon: <FileText className="h-4 w-4" />, color: 'text-gray-400' },
  cfg: { icon: <FileText className="h-4 w-4" />, color: 'text-gray-400' },
  conf: { icon: <FileText className="h-4 w-4" />, color: 'text-gray-400' },
  pdf: { icon: <PDFIcon />, color: 'text-red-500' },
  png: { icon: <ImageIcon />, color: 'text-purple-500' },
  jpg: { icon: <ImageIcon />, color: 'text-purple-500' },
  jpeg: { icon: <ImageIcon />, color: 'text-purple-500' },
  gif: { icon: <ImageIcon />, color: 'text-purple-500' },
  svg: { icon: <ImageIcon />, color: 'text-purple-500' },
  webp: { icon: <ImageIcon />, color: 'text-purple-500' },
  bmp: { icon: <ImageIcon />, color: 'text-purple-500' },
  ico: { icon: <ImageIcon />, color: 'text-purple-500' },
};

export function getFileIcon(fileName: string, filePath?: string): React.ReactNode {
  const name = fileName.toLowerCase();

  // Only root-level SKILL.md files use the skill icon
  // Subdirectory SKILL.md files use the regular markdown icon
  if (name === 'skill.md' && (!filePath || !filePath.includes('/'))) {
    return <span className="text-purple-500"><SkillSVGIcon /></span>;
  }

  const lastDot = name.lastIndexOf('.');
  const ext = lastDot === -1 ? name : name.slice(lastDot + 1);
  
  const fileConfig = FILE_TYPE_ICONS[ext];
  if (fileConfig) {
    return <span className={fileConfig.color}>{fileConfig.icon}</span>;
  }
  
  if (name === 'dockerfile' || name.startsWith('dockerfile.')) {
    return <span className="text-blue-500"><FileCode className="h-4 w-4" /></span>;
  }
  if (name === 'makefile' || name.startsWith('makefile.')) {
    return <span className="text-gray-600"><FileCode className="h-4 w-4" /></span>;
  }
  if (name === 'license' || name.startsWith('license')) {
    return <span className="text-gray-500"><FileText className="h-4 w-4" /></span>;
  }
  if (name === '.gitignore' || name === '.env' || name.startsWith('.env.')) {
    return <span className="text-yellow-600"><FileCode className="h-4 w-4" /></span>;
  }
  
  return <span className="text-gray-400"><File className="h-4 w-4" /></span>;
}
