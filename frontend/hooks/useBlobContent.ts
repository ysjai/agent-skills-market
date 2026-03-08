'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { api } from '@/lib/api';
import { getErrorMessage, isAbortError } from '@/lib/errors';
import { logger } from '@/lib/logger';

export interface UseBlobContentOptions {
  blobId?: string;
  blobUrl?: string;
  onError?: (error: string) => void;
}

export interface UseBlobContentReturn {
  content: string;
  isLoading: boolean;
  error: string | null;
  reload: () => void;
}

export function useBlobContent(options: UseBlobContentOptions): UseBlobContentReturn {
  const { blobId, blobUrl, onError } = options;
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
      const url = blobUrl || `/blobs/${id}`;
      const response = await api.getBlob(url, {
        signal: controller.signal,
      });
      const text = await response.text();
      setContent(text);
    } catch (err) {
      // Handle cancellation errors silently
      if (isAbortError(err)) {
        return;
      }

      const errorMessage = getErrorMessage(err, 'Failed to load file content');
      setError(errorMessage);
      onError?.(errorMessage);
      logger.error('Error loading blob:', err);
    } finally {
      setIsLoading(false);
    }
  }, [blobUrl, onError]);

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
