'use client';

import * as React from 'react';
import { useTranslations } from 'next-intl';
import { AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';

interface FileTreeWarningsProps {
  windowsWarningFiles: string[];
}

export function FileTreeWarnings({ windowsWarningFiles }: FileTreeWarningsProps) {
  const t = useTranslations('files');
  const [showWarningDetails, setShowWarningDetails] = React.useState(false);

  if (windowsWarningFiles.length === 0) {
    return null;
  }

  return (
    <div className="mb-4 rounded-lg bg-yellow-50 px-3 py-3 text-sm">
      <div className="flex items-start gap-2">
        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-yellow-600" />
        <div className="flex-1 min-w-0">
          <p className="font-medium text-yellow-800">
            {t('windowsWarning.title', { count: windowsWarningFiles.length })}
          </p>
          <p className="mt-1 text-yellow-700">
            {t('windowsWarning.description')}
          </p>
          <button
            type="button"
            onClick={() => setShowWarningDetails(!showWarningDetails)}
            className="mt-2 flex items-center gap-1 text-xs text-yellow-600 hover:text-yellow-800"
          >
            {showWarningDetails ? (
              <>
                <ChevronUp className="h-3 w-3" /> {t('windowsWarning.hideDetails')}
              </>
            ) : (
              <>
                <ChevronDown className="h-3 w-3" /> {t('windowsWarning.showDetails')}
              </>
            )}
          </button>
          {showWarningDetails && (
            <ul className="mt-2 space-y-1 max-h-32 overflow-y-auto border-t border-yellow-200 pt-2">
              {windowsWarningFiles.map((path, index) => (
                <li key={index} className="font-mono text-xs text-yellow-700 break-all">
                  • {path}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
