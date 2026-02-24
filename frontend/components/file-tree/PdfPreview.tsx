'use client';

import { useEffect, useState } from 'react';
import { Loader2, FileText } from 'lucide-react';
import { api } from '@/lib/api';
import { logger } from '@/lib/logger';
import { isAbortError, getErrorMessage } from '@/lib/errors';

interface PdfPreviewProps {
  blobId: string;
  fileName: string;
  height?: string;
}

export function PdfPreview({ blobId, fileName, height = '80vh' }: PdfPreviewProps) {
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let objectUrl: string | null = null;
    const controller = new AbortController();

    const loadPdf = async () => {
      setLoading(true);
      setError(null);

      try {
        const blob = await api.getBlob(`/blobs/${blobId}`, {
          signal: controller.signal,
          params: { content_type: 'application/pdf' },
        });
        objectUrl = URL.createObjectURL(blob);
        setPdfUrl(objectUrl);
      } catch (err) {
        if (isAbortError(err)) {
          return;
        }

        const errorMessage = getErrorMessage(err, 'Failed to load PDF');
        setError(errorMessage);
        logger.error('Error loading PDF:', err);
        setLoading(false);
      }
    };

    loadPdf();

    return () => {
      controller.abort();
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [blobId]);

  const handleIframeLoad = () => {
    setLoading(false);
  };

  if (error) {
    return (
      <div
        className="flex items-center justify-center bg-white rounded-lg"
        style={{ height }}
      >
        <div className="text-center p-8">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-2">Unable to load PDF file</p>
          <p className="text-sm text-gray-400">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div
      className="relative bg-white rounded-lg overflow-hidden"
      style={{ height }}
    >
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-white z-10">
          <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
        </div>
      )}
      {pdfUrl && (
        <iframe
          src={pdfUrl}
          title={fileName}
          className="w-full h-full border-0"
          onLoad={handleIframeLoad}
        />
      )}
    </div>
  );
}
