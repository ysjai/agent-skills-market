'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Loader2, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { logger } from '@/lib/logger';
import { isAbortError } from '@/lib/errors';

interface ImagePreviewProps {
  blobId: string;
  fileName: string;
  height?: string;
  blobUrl?: string;
}

export function ImagePreview({
  blobId,
  fileName,
  height = '500px',
  blobUrl,
}: ImagePreviewProps) {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let objectUrl: string | null = null;
    const controller = new AbortController();

    const loadImage = async () => {
      try {
        const url = blobUrl || `/blobs/${blobId}`;
        const blob = await api.getBlob(url, {
          signal: controller.signal,
        });
        objectUrl = URL.createObjectURL(blob);
        setImageUrl(objectUrl);
      } catch (err) {
        if (isAbortError(err)) {
          return;
        }

        setError('Failed to load image');
        setLoading(false);
        logger.error('Error loading image:', err);
      }
    };

    loadImage();

    return () => {
      controller.abort();
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [blobId, blobUrl]);

  const handleImageLoad = () => {
    setLoading(false);
  };

  const handleImageError = () => {
    setLoading(false);
    setError('Failed to render image');
  };

  return (
    <div
      className={cn(
        'flex flex-col overflow-hidden'
      )}
      style={{ height }}
    >
      <div
        className="relative flex items-center justify-center bg-gray-100 h-full"
      >
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-100 z-10">
            <div className="flex items-center gap-2 text-gray-500">
              <Loader2 className="w-6 h-6 animate-spin" />
              <span className="text-sm">Loading image...</span>
            </div>
          </div>
        )}

        {error && (
          <div className="flex flex-col items-center gap-2 text-red-600">
            <AlertCircle className="w-8 h-8" />
            <span className="text-sm">{error}</span>
          </div>
        )}

        {imageUrl && !error && (
          <img
            src={imageUrl}
            alt={fileName}
            className="max-w-full max-h-full object-contain rounded"
            onLoad={handleImageLoad}
            onError={handleImageError}
          />
        )}
      </div>
    </div>
  );
}

export default ImagePreview;
