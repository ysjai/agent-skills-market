export function parseError(err: unknown): string {
  if (err instanceof Error) {
    return err.message;
  }
  if (err && typeof err === "object" && "message" in err) {
    return String((err as { message: unknown }).message);
  }
  return String(err);
}

export function isAbortError(err: unknown): boolean {
  return (
    err instanceof DOMException && err.name === "AbortError"
  );
}

export function getErrorMessage(err: unknown, fallback: string): string {
  if (isAbortError(err)) {
    return fallback;
  }
  const parsed = parseError(err);
  return parsed || fallback;
}

export function parseApiError(err: unknown): string {
  if (err && typeof err === 'object' && 'response' in err) {
    const response = (err as { response?: { data?: { detail?: unknown } } }).response;
    const detail = response?.data?.detail;
    
    if (Array.isArray(detail) && detail.length > 0) {
      const firstError = detail[0];
      if (firstError && typeof firstError === 'object' && 'msg' in firstError && 'loc' in firstError) {
        const loc = (firstError as { loc: unknown[] }).loc;
        const msg = (firstError as { msg: string }).msg;
        const field = loc[loc.length - 1];
        return `${field}: ${msg}`;
      }
      return JSON.stringify(detail);
    }
    
    if (typeof detail === 'string') {
      return detail;
    }
  }
  
  return parseError(err);
}
