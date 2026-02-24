'use client';

import { createPortal } from 'react-dom';

interface DialogPortalProps {
  children: React.ReactNode;
}

export function DialogPortal({ children }: DialogPortalProps) {
  if (typeof document === 'undefined') return null;
  return createPortal(children, document.body);
}
