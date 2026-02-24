
## T4.3 - FileTree Render Optimization

### Performance Optimization Pattern
When optimizing React component rendering, use this two-step approach:

1. **Wrap child component with React.memo**:
   ```typescript
   import { memo } from 'react';
   
   export const Component = memo(function Component(props) {
     // component logic
   });
   Component.displayName = 'Component';  // For React DevTools
   ```

2. **Wrap parent handlers with useCallback**:
   ```typescript
   import { useCallback } from 'react';
   
   const handleAction = useCallback((param) => {
     // handler logic
   }, [dependency1, dependency2]);
   ```

### Why Both Are Needed
- **React.memo alone**: Won't help if parent passes new function references on every render
- **useCallback alone**: Won't prevent re-renders if child isn't memoized
- **Together**: Stable callback references + memoized child = prevented unnecessary re-renders

### Dependency Array Best Practices
For useCallback dependencies, include:
- State setters from useState (stable, can omit but safer to include)
- Props that are used inside the callback
- Context values used inside the callback
- Functions from custom hooks used inside the callback

### FileTree Specific Optimizations
The file tree benefits greatly from these optimizations because:
- Large trees can have 100+ items
- Expanding/collapsing folders previously caused all children to re-render
- Now only affected items re-render

### Files Modified
- components/file-tree/FileTreeItem.tsx: Added memo wrapper
- components/file-tree/FileTree.tsx: Added useCallback to 8 handlers

Evidence: .sisyphus/evidence/t4-3-optimize.txt
Date: 2026-02-19
