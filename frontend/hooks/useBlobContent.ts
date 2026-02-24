'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { api } from '@/lib/api';
import { getErrorMessage } from '@/lib/errors';
import { logger } from '@/lib/logger';

export interface UseBlobContentOptions {
  blobId?: string;
  onError?: (error: string) => void;
}

export interface UseBlobContentReturn {
  content: string;
  isLoading: boolean;
  error: string | null;
  reload: () => void;
}

function isCancelError(err: unknown): boolean {
  if (err instanceof Error) {
    return err.name === 'AbortError' || err.message?.includes('aborted') || false;
  }
  if (err && typeof err === 'object') {
    const errObj = err as Record<string, unknown>;
    return errObj.name === 'AbortError' || errObj.type === 'cancelation';
  }
  return false;
}

export function useBlobContent(options: UseBlobContentOptions): UseBlobContentReturn {
  const { blobId, onError } = options;
  const [content, setContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const loadContent = useCallback(async (id: string) => {
    // Cancel any pending request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.getBlob(`/blobs/${id}`, {
        signal: controller.signal,
      });
      const text = await response.text();
      setContent(text);
    } catch (err) {
      // Handle cancellation errors silently
      if (isCancelError(err)) {
        return;
      }

      const errorMessage = getErrorMessage(err, 'Failed to load file content');
      setError(errorMessage);
      onError?.(errorMessage);
      logger.error('Error loading blob:', err);
    } finally {
      setIsLoading(false);
    }
  }, [onError]);

  const reload = useCallback(() => {
    if (blobId) {
      loadContent(blobId);
    }
  }, [blobId, loadContent]);

  // Load content when blobId changes
  useEffect(() => {
    if (blobId) {
      loadContent(blobId);
    }

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
        abortControllerRef.current = null;
      }
    };
  }, [blobId, loadContent]);

  return {
    content,
    isLoading,
    error,
    reload,
  };
}
