# Tree Upload Fix - Learnings

## Problem Analysis

The issue was that after uploading a file to a collapsed directory, the parent directory was not automatically expanded. 

### Root Cause

1. `fetchTree()` completely rebuilds the tree structure with new node IDs
2. The original code tried to use `toggleNode(parentNode)` after `fetchTree()`
3. `toggleNode` uses node `id` to find and toggle nodes
4. But after `fetchTree()`, the node IDs are completely new, so `toggleNode` couldn't find the matching node

The problematic flow:
```
1. Upload completes
2. await fetchTree() - nodes rebuilt with NEW ids
3. Find parentNode in new nodes (by path) - gets node with NEW id
4. toggleNode(parentNode) - tries to match by id, but toggleNode's closure
   still references old state, so it can't find the node
```

## Solution

Added a new `expandPath` method that expands nodes by **path** instead of by node **id**:

1. Added `expandPath` function in `useTreeOperations.ts`:
   - Uses `node.path` to find nodes instead of `node.id`
   - Only expands if node type is 'tree' (directory)
   - Saves expanded state after update

2. Updated `useFileTree.ts`:
   - Added `expandPath` to the return interface
   - Exported the function from the hook

3. Updated `useFileUpload.ts`:
   - Replaced `toggleNode` dependency with `expandPath`
   - Simplified the upload completion logic to directly call `expandPath(parentPath)`
   - Removed the complex setTimeout + findNode workaround

4. Updated `FileTree.tsx`:
   - Destructured `expandPath` from `useFileTree`
   - Passed it to `useFileUpload`

## Key Insights

- When working with React state that gets completely rebuilt (like tree nodes), relying on stable identifiers (paths) is more reliable than relying on generated IDs
- The original `toggleNode` function works correctly for user interactions because it operates on the current tree state
- But after `fetchTree()`, we need a different approach that works with the newly built tree

## Code Changes Summary

Files modified:
- `frontend/hooks/file-tree/useTreeOperations.ts` - Added expandPath function
- `frontend/hooks/file-tree/useFileTree.ts` - Exported expandPath
- `frontend/hooks/useFileUpload.ts` - Use expandPath instead of toggleNode
- `frontend/components/file-tree/FileTree.tsx` - Pass expandPath to useFileUpload

## Testing Checklist

- [x] TypeScript type check passes
- [ ] Test uploading to collapsed directory
- [ ] Verify parent directory auto-expands
- [ ] Verify file is selected and content displayed
- [ ] Test uploading to root (no parent to expand)
- [ ] Test uploading multiple files to same directory

---

## Update: Large File Upload Issue

### New Problem Discovered

After fixing the directory expansion issue, a new issue was found:
- Uploading large images (e.g., photos) to a directory
- The parent directory opens correctly ✓
- The right panel shows the uploaded image ✓
- **But**: The image file does NOT appear in the directory tree
- After refreshing the page, the file appears ✓

### Root Cause Analysis

This is a **race condition** issue:
1. Large files take longer to process on the backend
2. When `fetchTree()` is called after upload completion, the backend may not have finished saving the file to the database
3. So the tree returned by `fetchTree()` doesn't include the newly uploaded file
4. But the file was actually uploaded successfully (proven by the right panel being able to display it)
5. After refresh, `fetchTree()` returns the complete tree including the new file

### Solution

Instead of relying solely on `fetchTree()` to refresh the tree, we now immediately add the node to the tree after successful upload:

1. In `useFileUpload.ts` `processFileUpload` function:
   - After successful upload API call
   - Immediately call `_addNode()` to add the file to the tree
   - Keep the `fetchTree()` call for eventual consistency

```typescript
// Upload successful - immediately add node to tree
const uploadedEntry = response.entries.find((e) => e.path === filePath);
if (uploadedEntry?.blob_id) {
  lastUploadedFileRef.current = { path: filePath, blobId: uploadedEntry.blob_id };
}

// Immediately add node to tree to avoid race condition with fetchTree
_addNode({
  path: filePath,
  blob_id: uploadedEntry?.blob_id || undefined,
  type: 'blob',
}, false);  // autoSelect=false to avoid interfering with multi-file upload
```

### Key Insights

- For time-sensitive UI updates, don't rely on server round-trips
- Use optimistic UI updates: immediately show the result in the UI, then sync with server
- `fetchTree()` is still needed for eventual consistency (in case another user modified the tree)
- The `_addNode` function handles parent directory lookup and sorting automatically

### Files Modified

- `frontend/hooks/useFileUpload.ts` - Added immediate `_addNode` call after upload success

### Build Status

✅ Build successful
