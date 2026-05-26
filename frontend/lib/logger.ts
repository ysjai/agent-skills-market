const isDevelopment = process.env.NODE_ENV === 'development';

export const logger = {
  info: (...args: unknown[]) => {
    if (isDevelopment) {
      // eslint-disable-next-line no-console -- centralized dev logger output
      console.info('[INFO]', ...args);
    }
  },

  warn: (...args: unknown[]) => {
    if (isDevelopment) {
      console.warn('[WARN]', ...args);
    }
  },

  error: (...args: unknown[]) => {
    console.error('[ERROR]', ...args);
  },
};
