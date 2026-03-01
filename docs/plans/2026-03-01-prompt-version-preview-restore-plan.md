# Prompt Version History Preview & Restore — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Allow users to preview any historical prompt version in the main editor area (full-size, read-only) and optionally restore it as unsaved changes.

**Architecture:** Add a `previewVersion` state to `PromptEditor` that, when set, replaces the normal toolbar with a preview banner and makes all fields read-only. `VersionHistory` gets an `onPreview` callback replacing the inline content expansion. Restore is a pure front-end state copy — no new API calls.

**Tech Stack:** React (useState), Next.js App Router, next-intl, Tailwind CSS, Monaco Editor (`readOnly` option), Lucide icons.

---

## Task 1: Add i18n keys for preview/restore UI

**Files:**
- Modify: `frontend/i18n/locales/en.json`
- Modify: `frontend/i18n/locales/zh.json`

**Step 1: Add keys to en.json**

Open `frontend/i18n/locales/en.json`. Find the `"prompts"` object. Add these 4 keys **before** the closing `}` of that object:

```json
"preview": "Preview",
"previewingVersion": "Previewing Version {number}",
"closePreview": "Close Preview",
"restoreThisVersion": "Restore This Version"
```

**Step 2: Add keys to zh.json**

Open `frontend/i18n/locales/zh.json`. Find the `"prompts"` object. Add:

```json
"preview": "预览",
"previewingVersion": "正在预览版本 {number}",
"closePreview": "关闭预览",
"restoreThisVersion": "还原至此版本"
```

**Step 3: Verify no build error**

```bash
cd frontend && npx tsc --noEmit 2>&1 | head -20
```
Expected: no errors related to missing keys.

**Step 4: Commit**

```bash
git add frontend/i18n/locales/en.json frontend/i18n/locales/zh.json
git commit -m "feat: add i18n keys for version preview/restore"
```

---

## Task 2: Update `VersionHistory` component — add `onPreview` prop, replace inline expansion with Preview button

**Files:**
- Modify: `frontend/components/prompts/VersionHistory.tsx`

**Step 1: Read the current file**

Read `frontend/components/prompts/VersionHistory.tsx` in full (122 lines).

**Step 2: Rewrite the component**

Replace the entire file content with the following. Key changes:
- Remove `expandedId` state and `toggleExpand` function
- Add `onPreview: (version: PromptVersion) => void` to `VersionHistoryProps`
- Remove `ChevronDown`, `ChevronUp`, `FileText` imports; add `Eye`
- Each version row: show version badge + title + date, plus a `[Preview]` button on the right

```tsx
'use client';

import React from 'react';
import { useTranslations } from 'next-intl';
import { History, Clock, LayoutTemplate, Eye } from 'lucide-react';

import { cn } from '@/lib/utils';
import { PromptVersion } from '@/types/prompt';

export interface VersionHistoryProps {
  versions: PromptVersion[];
  onPreview: (version: PromptVersion) => void;
}

export function VersionHistory({ versions, onPreview }: VersionHistoryProps) {
  const t = useTranslations('prompts');

  return (
    <div className="w-72 shrink-0 border-l border-gray-200 bg-white flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="flex shrink-0 items-center gap-2 p-4 pb-3 border-b border-gray-100">
        <History className="h-4 w-4 text-gray-500" />
        <h2 className="text-sm font-semibold tracking-tight text-gray-900">{t('versionHistory')}</h2>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto px-2 py-3 space-y-1 custom-scrollbar">
        {versions.length === 0 ? (
          <div className="flex h-32 flex-col items-center justify-center text-center px-4 mt-8">
            <LayoutTemplate className="h-8 w-8 text-gray-300 mb-2" />
            <p className="text-sm text-gray-500">{t('noVersions')}</p>
          </div>
        ) : (
          versions.map((version) => {
            const dateObj = new Date(version.created_at);
            const dateStr = `${dateObj.toLocaleDateString()} ${dateObj.toLocaleTimeString()}`;

            return (
              <div
                key={version.id}
                className="group flex items-center justify-between gap-2 rounded-xl border border-transparent px-3 py-2.5 hover:bg-gray-50 hover:border-gray-200 transition-all duration-150"
              >
                {/* Left: version info */}
                <div className="flex flex-col gap-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="inline-flex shrink-0 items-center justify-center rounded-full bg-gray-900 px-2 py-0.5 text-[10px] font-bold tracking-wide text-white shadow-sm">
                      {t('versionNumber', { number: version.version_number })}
                    </span>
                    <span className="truncate text-sm font-medium text-gray-800" title={version.title || t('untitled')}>
                      {version.title || t('untitled')}
                    </span>
                  </div>
                  <div className="flex items-center gap-1 text-gray-400">
                    <Clock className="h-3 w-3 shrink-0" />
                    <span className="text-[10px] font-medium tracking-wide">{dateStr}</span>
                  </div>
                </div>

                {/* Right: preview button */}
                <button
                  type="button"
                  onClick={() => onPreview(version)}
                  className={cn(
                    "shrink-0 flex items-center gap-1 rounded-lg border border-gray-200 bg-white px-2 py-1",
                    "text-xs font-medium text-gray-600 hover:bg-gray-900 hover:text-white hover:border-gray-900",
                    "transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-1"
                  )}
                >
                  <Eye className="h-3 w-3" />
                  {t('preview')}
                </button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
```

**Step 3: Check for TypeScript errors**

```bash
cd frontend && npx tsc --noEmit 2>&1 | grep VersionHistory
```
Expected: no errors.

**Step 4: Commit**

```bash
git add frontend/components/prompts/VersionHistory.tsx
git commit -m "feat: replace inline version expansion with Preview button in VersionHistory"
```

---

## Task 3: Update `PromptEditor` — add preview state, banner, read-only mode, restore handler

**Files:**
- Modify: `frontend/components/prompts/PromptEditor.tsx`

**Step 1: Read the current file**

Read `frontend/components/prompts/PromptEditor.tsx` in full (290 lines).

**Step 2: Add imports**

At the top of the file, the current import from `lucide-react` is:
```tsx
import { Save, UploadCloud, LayoutTemplate, Loader2, History } from 'lucide-react';
```

Change it to add `Eye`, `RotateCcw`, `X`, `Clock`:
```tsx
import { Save, UploadCloud, LayoutTemplate, Loader2, History, Eye, RotateCcw, X, Clock } from 'lucide-react';
```

**Step 3: Add `tPrompts` for full prompts namespace (already `t` exists) and add `previewVersion` state**

After the existing state declarations (around line 30, after `setShowVersionHistory`), add:

```tsx
const [previewVersion, setPreviewVersion] = useState<PromptVersion | null>(null);
```

Also add the prompts translator — currently `t = useTranslations('prompts')` already exists, so `t('preview')` etc. will work fine.

**Step 4: Add `handleRestoreVersion` function**

After the `handlePublish` function (around line 111), add:

```tsx
const handleRestoreVersion = () => {
  if (!previewVersion) return;
  setTitle(previewVersion.title || '');
  setDescription(previewVersion.description || '');
  setContent(previewVersion.content || '');
  setTags(previewVersion.tags || []);
  setPreviewVersion(null);
};
```

**Step 5: Replace the header toolbar with conditional rendering**

The current header block (lines ~138–191) is:
```tsx
{/* Header Controls */}
<div className="shrink-0 border-b border-gray-100 bg-white/50 backdrop-blur-xl z-10 py-4">
  <div className="flex items-center justify-between w-full px-4 sm:px-6">
    ...normal toolbar...
  </div>
</div>
```

Replace the **inner** `<div className="flex items-center justify-between...">` and its contents with this conditional block:

```tsx
{previewVersion ? (
  /* Preview Banner */
  <div className="flex items-center justify-between w-full px-4 sm:px-6">
    <div className="flex items-center gap-2 text-amber-700">
      <Clock className="h-4 w-4 shrink-0" />
      <span className="text-sm font-medium">
        {t('previewingVersion', { number: previewVersion.version_number })}
      </span>
      <span className="text-xs text-amber-600">
        · {new Date(previewVersion.created_at).toLocaleString()}
      </span>
    </div>
    <div className="flex items-center gap-2">
      <Button
        variant="outline"
        onClick={() => setPreviewVersion(null)}
        className="min-w-[120px]"
      >
        <X className="h-4 w-4 mr-1.5" />
        {t('closePreview')}
      </Button>
      <Button
        variant="default"
        onClick={handleRestoreVersion}
        className="bg-gray-900 hover:bg-gray-800 text-white min-w-[170px]"
      >
        <RotateCcw className="h-4 w-4 mr-1.5" />
        {t('restoreThisVersion')}
      </Button>
    </div>
  </div>
) : (
  /* Normal Toolbar */
  <div className="flex items-center justify-between w-full px-4 sm:px-6">
    <div className="flex items-center gap-3">
      <h2 className="text-lg font-semibold text-gray-900 tracking-tight">
        {tCommon('edit')} Prompt
      </h2>
      <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">
        {t('versionNumber', { number: selectedPrompt.version })}
      </span>
      {hasChanges && (
        <span className="text-xs font-medium text-amber-600 bg-amber-50 px-2 py-1 rounded-full">
          Unsaved changes
        </span>
      )}
    </div>
    <div className="flex items-center gap-2">
      <Button
        variant="outline"
        onClick={handleSave}
        disabled={!hasChanges || isSaving || isPublishing}
        className="min-w-[100px]"
      >
        {isSaving ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Save className="h-4 w-4 mr-1.5" />
        )}
        {tCommon('save')}
      </Button>
      <Button
        variant="default"
        onClick={handlePublish}
        disabled={isSaving || isPublishing}
        className="bg-gray-900 hover:bg-gray-800 text-white min-w-[140px]"
      >
        {isPublishing ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <UploadCloud className="h-4 w-4 mr-1.5" />
        )}
        {t('publishVersion')}
      </Button>
      <Button
        variant="outline"
        onClick={() => setShowVersionHistory(!showVersionHistory)}
        className="min-w-[100px]"
        title={t('versionHistory')}
      >
        <History className="h-4 w-4 mr-1.5" />
        {t('versionHistory')}
      </Button>
    </div>
  </div>
)}
```

Also change the outer wrapper `<div className="shrink-0 border-b border-gray-100 bg-white/50 backdrop-blur-xl z-10 py-4">` to include the amber background conditionally:

```tsx
<div className={cn(
  "shrink-0 border-b z-10 py-4",
  previewVersion
    ? "bg-amber-50 border-amber-200"
    : "bg-white/50 backdrop-blur-xl border-gray-100"
)}>
```

**Step 6: Make form fields read-only in preview mode**

In the content area, add `disabled={!!previewVersion}` to:
- The title `<Input>` element
- The description `<textarea>` element
- The `<TagInput>` component (add `disabled` prop — check if TagInput accepts it; if not, wrap in a `pointer-events-none` div)

**Step 7: Make Monaco editor read-only in preview mode**

In the `<Editor>` options, change:
```tsx
options={{
  ...existing options...
  readOnly: !!previewVersion,
}}
```

Also update Monaco `value` to show preview content when in preview mode:
```tsx
value={previewVersion ? previewVersion.content : content}
onChange={(val) => {
  if (!previewVersion) setContent(val || '');
}}
```

Similarly update the title/description/tags displayed values:
- Title Input `value`: `previewVersion ? previewVersion.title : title`
- Description textarea `value`: `previewVersion ? (previewVersion.description || '') : description`
- TagInput `tags`: `previewVersion ? (previewVersion.tags || []) : tags`

**Step 8: Pass `onPreview` to `VersionHistory`**

Find the `<VersionHistory>` usage (near line 285):
```tsx
<VersionHistory versions={versions} />
```
Change to:
```tsx
<VersionHistory versions={versions} onPreview={setPreviewVersion} />
```

**Step 9: Reset `previewVersion` when selected prompt changes**

In the `useEffect` that syncs state when `selectedPrompt` changes, add:
```tsx
setPreviewVersion(null);
```
to both the `if (selectedPrompt)` and `else` branches.

**Step 10: TypeScript check**

```bash
cd frontend && npx tsc --noEmit 2>&1 | grep PromptEditor
```
Expected: no errors.

**Step 11: Commit**

```bash
git add frontend/components/prompts/PromptEditor.tsx
git commit -m "feat: add version preview mode and restore to PromptEditor"
```

---

## Task 4: Check TagInput for `disabled` prop support

**Files:**
- Read: `frontend/components/prompts/TagInput.tsx`

**Step 1: Read TagInput**

Read `frontend/components/prompts/TagInput.tsx`.

**Step 2: If `disabled` prop not supported**

If `TagInput` doesn't accept a `disabled` prop, wrap it in preview mode like this instead:
```tsx
<div className={cn(previewVersion ? "pointer-events-none opacity-60" : "")}>
  <TagInput tags={previewVersion ? (previewVersion.tags || []) : tags} onChange={setTags} />
</div>
```

If `TagInput` already has `disabled`, just pass `disabled={!!previewVersion}`.

**Step 3: Commit only if TagInput was modified**

```bash
git add frontend/components/prompts/TagInput.tsx
git commit -m "feat: add disabled prop to TagInput for preview mode"
```

---

## Task 5: Manual verification

**Step 1: Open the app**

Navigate to `http://localhost:3001` in the browser (frontend runs on port 3001).

**Step 2: Log in**
- Email: `test@example.com`
- Password: `password123`

**Step 3: Go to Prompts page**

Click "My Prompts" in the user dropdown.

**Step 4: Select a prompt that has version history**

Click any prompt in the list. Click "Version History" button in the toolbar to open the sidebar.

If no versions exist, click "Publish Version" first to create one, then re-open version history.

**Step 5: Test Preview**

Click the "Preview" button on a version row.
Verify:
- Header bar turns amber-tinted with "Previewing Version N · date" text
- "Close Preview" and "Restore This Version" buttons appear
- Title, description, and content fields are disabled/read-only showing the version's data
- Tags show the version's tags (read-only)
- Monaco editor is read-only

**Step 6: Test Close Preview**

Click "Close Preview". Verify editor returns to normal editing state with current prompt's data.

**Step 7: Test Restore**

Open preview of an old version. Click "Restore This Version".
Verify:
- Editor returns to normal editing state
- Fields now show the old version's values
- "Unsaved changes" badge appears in the header
- Save button is enabled

**Step 8: Save the restored version**

Click Save to confirm the restore persists.
