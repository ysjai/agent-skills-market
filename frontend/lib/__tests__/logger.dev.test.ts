import { describe, it, expect, beforeEach, afterEach, spyOn } from 'bun:test';

// Set environment BEFORE importing logger
process.env.NODE_ENV = 'development';

// Import logger after setting env
const { logger } = await import('../logger');

describe('logger - Development environment', () => {
  let infoSpy: ReturnType<typeof spyOn>;
  let warnSpy: ReturnType<typeof spyOn>;
  let errorSpy: ReturnType<typeof spyOn>;

  beforeEach(() => {
    infoSpy = spyOn(console, 'info').mockImplementation(() => {});
    warnSpy = spyOn(console, 'warn').mockImplementation(() => {});
    errorSpy = spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    infoSpy.mockRestore();
    warnSpy.mockRestore();
    errorSpy.mockRestore();
  });

  it('should call console.info with [INFO] prefix', () => {
    logger.info('test message');
    expect(infoSpy).toHaveBeenCalledTimes(1);
    expect(infoSpy).toHaveBeenCalledWith('[INFO]', 'test message');
  });

  it('should call console.info with multiple arguments', () => {
    logger.info('message1', 'message2', { key: 'value' });
    expect(infoSpy).toHaveBeenCalledTimes(1);
    expect(infoSpy).toHaveBeenCalledWith('[INFO]', 'message1', 'message2', { key: 'value' });
  });

  it('should call console.warn with [WARN] prefix', () => {
    logger.warn('warning message');
    expect(warnSpy).toHaveBeenCalledTimes(1);
    expect(warnSpy).toHaveBeenCalledWith('[WARN]', 'warning message');
  });

  it('should call console.warn with multiple arguments', () => {
    logger.warn('warn1', 'warn2', 123);
    expect(warnSpy).toHaveBeenCalledTimes(1);
    expect(warnSpy).toHaveBeenCalledWith('[WARN]', 'warn1', 'warn2', 123);
  });

  it('should call console.error with [ERROR] prefix', () => {
    logger.error('error message');
    expect(errorSpy).toHaveBeenCalledTimes(1);
    expect(errorSpy).toHaveBeenCalledWith('[ERROR]', 'error message');
  });

  it('should call console.error with multiple arguments', () => {
    logger.error('error1', 'error2', new Error('test'));
    expect(errorSpy).toHaveBeenCalledTimes(1);
    expect(errorSpy).toHaveBeenCalledWith('[ERROR]', 'error1', 'error2', new Error('test'));
  });
});
