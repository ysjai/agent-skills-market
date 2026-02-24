'use client';

import { useState, useRef, useLayoutEffect } from 'react';
import { cn } from '@/lib/utils';
import { Button } from './Button';

interface InputDialogProps {
  open: boolean;
  title: string;
  label: string;
  placeholder?: string;
  defaultValue?: string;
  error?: string;
  onConfirm: (value: string) => void;
  onCancel: () => void;
}

export function InputDialog({
  open,
  title,
  label,
  placeholder = '',
  defaultValue = '',
  error,
  onConfirm,
  onCancel,
}: InputDialogProps) {
  const [value, setValue] = useState(defaultValue);
  const inputRef = useRef<HTMLInputElement>(null);
  const prevOpenRef = useRef(open);

  useLayoutEffect(() => {
    if (open && !prevOpenRef.current) {
      // Use flushSync to batch the state update
      setValue(defaultValue);
    }
    prevOpenRef.current = open;
    
    if (open) {
      const timer = setTimeout(() => inputRef.current?.focus(), 100);
      return () => clearTimeout(timer);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && value.trim()) {
      onConfirm(value.trim());
    } else if (e.key === 'Escape') {
      onCancel();
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onCancel} />
      <div className="relative bg-white rounded-lg shadow-xl w-80 p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {label}
          </label>
          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className={cn(
              'w-full px-3 py-2 border rounded-md text-sm',
              error ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-gray-500'
            )}
          />
          {error && (
            <p className="mt-1 text-sm text-red-600">{error}</p>
          )}
        </div>
        <div className="flex justify-end gap-2">
          <Button variant="outline" size="sm" onClick={onCancel}>
            Cancel
          </Button>
          <Button
            size="sm"
            onClick={() => value.trim() && onConfirm(value.trim())}
            disabled={!value.trim()}
          >
            Confirm
          </Button>
        </div>
      </div>
    </div>
  );
}
