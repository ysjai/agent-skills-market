'use client';

import { useState } from 'react';
import { useRouter } from '@/i18n/routing';
import { useTranslations } from 'next-intl';
import { FolderUp, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';
import { Dialog } from '@/components/ui/Dialog';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { ProgressDialog, type ProgressItem } from '@/components/ui/ProgressDialog';
import { api } from '@/lib/api';
import { parseApiError } from '@/lib/errors';
import type { Skill, CreateSkillRequest } from '@/types/skill';
import { getFileType } from '@/lib/file-utils';
import { hasWindowsReservedChars } from '@/lib/windows-fs';

interface ImportSkillDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: (skill: Skill) => void;
}

export function ImportSkillDialog({ open, onClose, onSuccess }: ImportSkillDialogProps) {
  const router = useRouter();
  const tForm = useTranslations('skillForm');
  const tImport = useTranslations('import');
  const tCommon = useTranslations('common');
  const tProgress = useTranslations('progress');

  const [selectedDirName, setSelectedDirName] = useState('');
  const [importStep, setImportStep] = useState<'select' | 'confirm'>('select');
  const [form, setForm] = useState({
    name: '',
    slug: '',
    description: '',
  });
  const [files, setFiles] = useState<Array<{
    path: string;
    content?: string;
    file?: File;
    type: 'blob' | 'tree';
  }>>([]);
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState('');
  const [fileWarnings, setFileWarnings] = useState<string[]>([]);
  const [showWarningDetails, setShowWarningDetails] = useState(false);

  const [progressDialogOpen, setProgressDialogOpen] = useState(false);
  const [progressItems, setProgressItems] = useState<ProgressItem[]>([]);
  const [progressCurrent, setProgressCurrent] = useState(0);
  const [progressTotal, setProgressTotal] = useState(0);
  const [progressCurrentFile, setProgressCurrentFile] = useState('');
  const [importError, setImportError] = useState('');
  const [slugError, setSlugError] = useState('');

  const hasChinese = (text: string) => /[\u4e00-\u9fa5]/.test(text);

  const generateSlug = (name: string) => {
    if (hasChinese(name)) return '';
    return name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
  };

  const parseSkillMd = (content: string): { name?: string; description?: string } => {
    const frontMatterMatch = content.match(/^---\s*\n([\s\S]*?)\n---/);
    if (!frontMatterMatch) return {};
    
    const frontMatter = frontMatterMatch[1];
    const result: { name?: string; description?: string } = {};
    
    const nameMatch = frontMatter.match(/^name:\s*(.+)$/m);
    if (nameMatch) {
      result.name = nameMatch[1].trim();
    }
    
    const descMatch = frontMatter.match(/^description:\s*(.+)$/m);
    if (descMatch) {
      result.description = descMatch[1].trim();
    }
    
    return result;
  };

  const handleDirectorySelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = e.target.files;
    if (!fileList || fileList.length === 0) return;

    setError('');
    const fileArray = Array.from(fileList);
    const dirName = fileArray[0].webkitRelativePath.split('/')[0];
    setSelectedDirName(dirName);

    let skillMdFile: File | null = null;
    const fileEntries: Array<{ path: string; content?: string; file?: File; type: 'blob' }> = [];
    const directories = new Set<string>();

    for (const file of fileArray) {
      const relativePath = file.webkitRelativePath.replace(`${dirName}/`, '');

      if (relativePath === 'SKILL.md') {
        skillMdFile = file;
      }

      if (file.name.startsWith('.')) continue;

      const parts = relativePath.split('/');
      for (let i = 1; i < parts.length; i++) {
        directories.add(parts.slice(0, i).join('/'));
      }

      try {
        const fileType = getFileType(file.name);
        if (fileType === 'text') {
          const content = await file.text();
          fileEntries.push({
            path: relativePath,
            content,
            type: 'blob',
          });
        } else {
          fileEntries.push({
            path: relativePath,
            file,
            type: 'blob',
          });
        }
      } catch {
        // Silently ignore file read errors during import scanning
      }
    }

    if (!skillMdFile) {
      setError(tImport('errors.skillMdNotFound'));
      return;
    }

    const skillMdContent = await skillMdFile.text();
    const metadata = parseSkillMd(skillMdContent);

    if (!metadata.name || !metadata.description) {
      const missing = [];
      if (!metadata.name) missing.push('name');
      if (!metadata.description) missing.push('description');
      setError(tImport('errors.missingFields', { fields: missing.join(', ') }));
      return;
    }

    const sortedDirs = Array.from(directories).sort((a, b) => {
      const depthA = a.split('/').length;
      const depthB = b.split('/').length;
      return depthA - depthB;
    });

    const dirEntries = sortedDirs.map(dir => ({
      path: dir,
      type: 'tree' as const,
    }));

    const sortedFileEntries = fileEntries.sort((a, b) => a.path.localeCompare(b.path));

    const allEntries = [...dirEntries, ...sortedFileEntries];

    const slug = generateSlug(metadata.name);

    const warnings = sortedFileEntries
      .filter(f => hasWindowsReservedChars(f.path))
      .map(f => f.path);
    setFileWarnings(warnings);

    setForm({
      name: metadata.name,
      slug: slug || '',
      description: metadata.description,
    });
    setFiles(allEntries);

    // Check for duplicate immediately when entering the form
    if (slug) {
      try {
        const exists = await checkSkillExists(slug);
        if (exists) {
          setSlugError(tImport('errors.identifierExists', { name: slug }));
        }
      } catch {
      }
    } else {
      setSlugError(tForm('invalidName'));
    }

    setImportStep('confirm');
  };

  const checkSkillExists = async (slug: string): Promise<boolean> => {
    try {
      const response = await api.get<{ items?: Skill[] }>('/skills');
      const skills = response?.items || [];
      return skills.some((skill: Skill) => skill.slug === slug);
    } catch {
      return false;
    }
  };

  const executeImport = async () => {
    if (!form.name.trim() || !form.slug.trim()) return;

    setImporting(true);
    setError('');
    setImportError('');

    const slug = generateSlug(form.name.trim());
    if (!slug) {
      setImportError(tForm('invalidName'));
      setImporting(false);
      return;
    }
    const fileEntries = files.filter(f => f.type === 'blob');
    const totalFiles = fileEntries.length;

    setProgressDialogOpen(true);
    setProgressItems(fileEntries.map(f => ({ name: f.path, status: 'pending' })));
    setProgressTotal(totalFiles);
    setProgressCurrent(0);
    setProgressCurrentFile('');

    try {
      const trimmedDescription = form.description.trim();
      if (!trimmedDescription) {
        setError('Description is required');
        setImporting(false);
        return;
      }

      const data: CreateSkillRequest = {
        name: form.name.trim().toLowerCase().replace(/\s+/g, '-'),
        slug: slug,
        description: trimmedDescription,
      };

      const newSkill = await api.post<Skill>('/skills/import', data);

      if (newSkill.tree_id && files.length > 0) {
        const entriesWithBlobIds: Array<{ path: string; type: 'blob' | 'tree'; content?: string; blob_id?: string }> = [];

        const dirEntries = files.filter(f => f.type === 'tree');
        for (const dir of dirEntries) {
          entriesWithBlobIds.push({
            path: dir.path,
            type: 'tree',
          });
        }

        for (let i = 0; i < fileEntries.length; i++) {
          const f = fileEntries[i];
          
          setProgressCurrentFile(f.path);
          setProgressItems(prev =>
            prev.map((item, idx) => idx === i ? { ...item, status: 'processing' } : item)
          );

          try {
            if (f.file) {
              const formData = new FormData();
              formData.append('file', f.file);
              const blobResponse = await api.post<{
                id: string;
                content_hash: string;
                size: number;
                compressed: boolean;
                created_at: string;
              }>('/blobs', formData);
              entriesWithBlobIds.push({
                path: f.path,
                type: 'blob',
                blob_id: blobResponse.id,
              });
            } else {
              entriesWithBlobIds.push({
                path: f.path,
                type: 'blob',
                content: f.content,
              });
            }

            setProgressItems(prev =>
              prev.map((item, idx) => idx === i ? { ...item, status: 'success' } : item)
            );
          } catch (err) {
            const errorMessage = err instanceof Error ? err.message : String(err);
            setProgressItems(prev =>
              prev.map((item, idx) => idx === i ? { ...item, status: 'error', error: errorMessage } : item)
            );
          }

          setProgressCurrent(i + 1);
        }

        await api.post(`/trees/${newSkill.tree_id}/files/folder`, {
          base_path: '',
          entries: entriesWithBlobIds,
        });
      }

      setTimeout(() => {
        setProgressDialogOpen(false);
        
        if (onSuccess) {
          onSuccess(newSkill);
        }

        onClose();
        resetState();
        router.push(`/skills/${newSkill.id}`);
      }, 1500);
    } catch (err: unknown) {
      const errorMessage = parseApiError(err);
      setImportError(errorMessage);
      setImporting(false);
    }
  };

  const handleImportSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) return;

    const slug = generateSlug(form.name.trim());
    if (!slug) {
      setError(tForm('invalidName'));
      return;
    }

    setImporting(true);
    setError('');
    setSlugError('');

    const exists = await checkSkillExists(slug);

    if (exists) {
      setError(tImport('errors.identifierExists', { name: slug }));
      setSlugError(tImport('errors.identifierExists', { name: slug }));
      setImporting(false);
      return;
    }

    await executeImport();
  };

  const resetState = () => {
    setError('');
    setImportError('');
    setSelectedDirName('');
    setImportStep('select');
    setForm({ name: '', slug: '', description: '' });
    setFiles([]);
    setFileWarnings([]);
    setShowWarningDetails(false);
    setProgressItems([]);
    setProgressCurrent(0);
    setProgressTotal(0);
    setProgressCurrentFile('');
    setSlugError('');
  };

  const handleClose = () => {
    if (!importing) {
      onClose();
      resetState();
    }
  };

  const handleProgressCancel = () => {
    setProgressDialogOpen(false);
  };

  const handleProgressClose = () => {
    setProgressDialogOpen(false);
    if (progressCurrent >= progressTotal && progressTotal > 0) {
      onClose();
      resetState();
    }
  };

  return (
    <>
      <Dialog
        open={open}
        onClose={handleClose}
        title={importStep === 'select' ? tImport('title') : tImport('confirmTitle')}
      >
      {importStep === 'select' ? (
        <div className="space-y-4">
          <p className="text-sm text-gray-600 sm:text-base">
            {tImport('selectDirectory')}
          </p>
          {error && (
            <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
              {error}
            </div>
          )}
          <div className="relative flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 p-6 sm:p-8">
            <FolderUp className="mb-2 h-8 w-8 text-gray-400 sm:h-10 sm:w-10" />
            <p className="mb-2 text-sm text-gray-500">{tImport('clickToSelect')}</p>
            <input
              type="file"
              // @ts-expect-error webkitdirectory is non-standard but widely supported
              webkitdirectory=""
              onChange={handleDirectorySelect}
              disabled={importing}
              className="absolute inset-0 cursor-pointer opacity-0 disabled:cursor-not-allowed"
            />
            <Button variant="outline" className="pointer-events-none relative z-10 min-h-[44px]" disabled={importing}>
              {tImport('title')}
            </Button>
          </div>
          <div className="flex flex-col gap-2 sm:flex-row sm:justify-end">
            <Button
              variant="outline"
              onClick={handleClose}
              disabled={importing}
              className="min-h-[44px] w-full sm:w-auto"
            >
              {tCommon('cancel')}
            </Button>
          </div>
        </div>
      ) : (
        <form onSubmit={handleImportSkill} className="space-y-4">
          <div className="mb-4 rounded-lg bg-green-50 px-3 py-2 text-sm text-green-700">
            {tImport('selectedFiles', { name: selectedDirName, count: files.filter(f => f.type === 'blob').length })}
          </div>

          {fileWarnings.length > 0 && (
            <div className="rounded-lg bg-yellow-50 px-3 py-3 text-sm">
              <div className="flex items-start gap-2">
                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-yellow-600" />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-yellow-800">
                    {tImport('windowsWarning.title', { count: fileWarnings.length })}
                  </p>
                  <p className="mt-1 text-yellow-700">
                    {tImport('windowsWarning.description')}
                  </p>
                  {fileWarnings.length > 0 && (
                    <button
                      type="button"
                      onClick={() => setShowWarningDetails(!showWarningDetails)}
                      className="mt-2 flex items-center gap-1 text-xs text-yellow-600 hover:text-yellow-800"
                    >
                      {showWarningDetails ? (
                        <>
                          <ChevronUp className="h-3 w-3" /> {tImport('windowsWarning.hideDetails')}
                        </>
                      ) : (
                        <>
                          <ChevronDown className="h-3 w-3" /> {tImport('windowsWarning.showDetails')}
                        </>
                      )}
                    </button>
                  )}
                  {showWarningDetails && (
                    <ul className="mt-2 space-y-1 max-h-32 overflow-y-auto border-t border-yellow-200 pt-2">
                      {fileWarnings.map((path, index) => (
                        <li key={index} className="font-mono text-xs text-yellow-700 break-all">
                          • {path}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
              {error}
            </div>
          )}
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700 sm:mb-2">
              {tForm('name')}
            </label>
            <Input
              value={form.name}
              onChange={async (e) => {
                const name = e.target.value;
                const slug = generateSlug(name);
                setForm(prev => ({ ...prev, name, slug }));
                setError('');

                if (slug && name.trim()) {
                  const exists = await checkSkillExists(slug);
                  if (exists) {
                    setSlugError(tImport('errors.identifierExists', { name: slug }));
                  } else {
                    setSlugError('');
                  }
                } else {
                  setSlugError('');
                }
              }}
              disabled={importing}
              required
              autoFocus
              title={tForm('nameHelp')}
              className={`min-h-[44px] ${slugError ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}`}
            />
            {slugError && (
              <p className="mt-1.5 text-sm text-red-600">
                {slugError}
              </p>
            )}
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700 sm:mb-2">
              {tForm('slug')}
            </label>
            <Input
              value={form.slug}
              readOnly
              disabled={true}
              className="min-h-[44px] bg-gray-100 cursor-not-allowed"
            />
            <p className="mt-1.5 text-xs text-gray-500">
              {tForm('slugHelp')}
            </p>
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700 sm:mb-2">
              {tForm('description')}
            </label>
            <Input
              placeholder={tForm('descriptionPlaceholder')}
              value={form.description}
              onChange={(e) => setForm(prev => ({ ...prev, description: e.target.value }))}
              disabled={importing}
              className="min-h-[44px]"
            />
          </div>
          <div className="flex flex-col gap-2 pt-2 sm:flex-row sm:gap-3">
            <Button
              type="button"
              variant="outline"
              className="min-h-[44px] flex-1"
              onClick={() => {
                setImportStep('select');
                setError('');
              }}
              disabled={importing}
            >
              {tImport('back')}
            </Button>
            <Button
              type="submit"
              className="min-h-[44px] flex-1"
              disabled={importing || !form.name.trim() || !/^[a-z0-9-]+$/.test(form.name.trim()) || !!slugError}
            >
              {importing ? (
                <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                  {tForm('importing')}
                </>
              ) : (
                tImport('confirmImport')
              )}
            </Button>
          </div>
        </form>
      )}
    </Dialog>

    <ProgressDialog
      open={progressDialogOpen}
      type="upload"
      title={tProgress('importingSkill')}
      current={progressCurrent}
      total={progressTotal}
      currentFile={progressCurrentFile}
      items={progressItems}
      error={importError}
      onCancel={handleProgressCancel}
      onClose={handleProgressClose}
    />
  </>
  );
}
