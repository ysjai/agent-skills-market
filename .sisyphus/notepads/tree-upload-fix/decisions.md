# Tree Upload Fix - Decisions

## Decision 1: Use path-based expansion instead of id-based

**Context**: The original `toggleNode` function used node `id` to find and toggle nodes. After `fetchTree()`, all node IDs are regenerated, making the id-based approach unreliable.

**Decision**: Create a new `expandPath` function that uses `node.path` instead of `node.id`.

**Rationale**: 
- Paths are stable identifiers that persist across tree rebuilds
- The upload logic already knows the parent path, so no lookup is needed
- Simpler and more direct than trying to coordinate between old and new node references

## Decision 2: Keep toggleNode for UI interactions

**Context**: The existing `toggleNode` function is used when users click to expand/collapse directories.

**Decision**: Keep `toggleNode` unchanged and add `expandPath` as a new function.

**Rationale**:
- `toggleNode` works correctly for its use case (user interactions on current tree)
- Adding a new function is less risky than modifying existing behavior
- `toggleNode` uses id which is fine for immediate user interactions
- `expandPath` is specifically for programmatic expansion after tree rebuilds

## Decision 3: Remove toggleNode from useFileUpload dependencies

**Context**: After switching to `expandPath`, `toggleNode` was no longer used in `useFileUpload`.

**Decision**: Remove `toggleNode` from the `UseFileUploadOptions` interface and from the hook parameters.

**Rationale**:
- Cleaner API - only expose what's needed
- TypeScript error forced this cleanup (unused parameter)
- Reduces coupling between hooks

## Decision 4: Only expand directories (type === 'tree')

**Context**: The `expandPath` function could theoretically be called with any path.

**Decision**: Add a type check in `expandPath` to only expand nodes where `type === 'tree'`.

**Rationale**:
- Files cannot be "expanded" in the tree view
- Prevents accidental misuse
- Matches the semantic meaning of "expansion"
