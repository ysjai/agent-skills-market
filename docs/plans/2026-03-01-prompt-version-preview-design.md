# Design: Prompt Version History Preview & Restore

**Date**: 2026-03-01  
**Status**: Approved  
**Scope**: Frontend only — `VersionHistory.tsx`, `PromptEditor.tsx`

---

## Problem

The current `VersionHistory` sidebar panel shows each version's content in a tiny `max-h-48` scrollable box, which:
- Cannot display long content without truncation
- Has no way to restore a previous version
- Provides a poor reading experience

## Goal

Allow users to:
1. **Preview** any historical version in the main editor area (full-size, read-only)
2. **Restore** a version by loading its content into the editor as unsaved changes
3. **Close** the preview to return to normal editing

---

## User Interaction Flow

```
VersionHistory sidebar
  └─ Version item row (shows: version number, date)
       └─ [Preview] button
            │
            ▼
PromptEditor enters "preview mode"
  ├─ Header toolbar replaced with preview banner:
  │    "Previewing v3 · 2026-02-28 15:30  [Close Preview]  [Restore This Version]"
  ├─ All form fields become read-only
  └─ Monaco editor becomes readOnly: true

User clicks [Restore This Version]
  └─ title, description, content, tags all replaced with version's values
  └─ Preview mode exits
  └─ hasChanges = true (unsaved changes indicator appears)
  └─ User can now Save or Publish as normal

User clicks [Close Preview]
  └─ Preview mode exits
  └─ Editor restores to current prompt's values unchanged
```

---

## Architecture

### State Changes in `PromptEditor`

New state variable:
```typescript
const [previewVersion, setPreviewVersion] = useState<PromptVersion | null>(null);
```

New handler:
```typescript
const handleRestoreVersion = () => {
  if (!previewVersion) return;
  setTitle(previewVersion.title || '');
  setDescription(previewVersion.description || '');
  setContent(previewVersion.content || '');
  setTags(previewVersion.tags || []);
  setPreviewVersion(null); // exit preview mode
};
```

### Conditional Rendering in Header Toolbar

```
if (previewVersion) → show "Preview Banner" (version info + Close + Restore buttons)
else                → show normal toolbar (Save, Publish Version, Version History buttons)
```

### Monaco Editor Read-Only Toggle

```typescript
options={{
  readOnly: previewVersion !== null,
  ...
}}
```

Form fields (title, description, tags) also use `disabled={previewVersion !== null}`.

---

## Component Interface Changes

### `VersionHistory.tsx`

**Before**: Each version row expands to show a tiny content preview box.  
**After**: Each version row shows a `[Preview]` button; no inline content expansion.

New prop added:
```typescript
interface VersionHistoryProps {
  versions: PromptVersion[];
  onPreview: (version: PromptVersion) => void;  // NEW
}
```

Visual change: Replace `ChevronDown/ChevronUp` toggle with an `Eye` icon button labeled "Preview".

### `PromptEditor.tsx`

Passes `onPreview={setPreviewVersion}` to `<VersionHistory>`.

---

## Preview Banner Design

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🕐 Previewing Version 3 · Feb 28, 2026 15:30          [Close]  [Restore This Version] │
└─────────────────────────────────────────────────────────────────────┘
```

- Background: `bg-amber-50 border-b border-amber-200`
- Left: clock icon + "Previewing Version N · date"
- Right: "Close Preview" (outline button) + "Restore This Version" (black button)

---

## What Does NOT Change

- No backend changes required
- No new API calls
- No new files needed
- Restore is purely a frontend state update (equivalent to user typing in the old content)
- The `VersionHistory` panel still opens/closes via the existing "Version History" button in the toolbar

---

## Files Modified

| File | Changes |
|------|---------|
| `frontend/components/prompts/VersionHistory.tsx` | Remove inline content expansion; add `onPreview` prop; add Preview button per row |
| `frontend/components/prompts/PromptEditor.tsx` | Add `previewVersion` state; conditional header banner; pass `onPreview` to `VersionHistory`; toggle `readOnly` on Monaco + form fields |

---

## i18n Keys Required

New keys to add in `messages/en.json` and `messages/zh.json` under `prompts`:

```json
"previewingVersion": "Previewing Version {number}",
"closePreview": "Close Preview",
"restoreThisVersion": "Restore This Version",
"preview": "Preview"
```
