import { describe, it, expect } from 'bun:test';

import { formatRelativeTime } from '../time';

type MockDateArgs = ConstructorParameters<typeof Date>;

// Helper to mock Date constructor
function mockDate(mockTimestamp: number) {
  const OriginalDate = global.Date;
  global.Date = class extends Date {
    constructor(...args: MockDateArgs) {
      if (args.length === 0) {
        super(mockTimestamp);
      } else {
        super(...args);
      }
    }
  } as unknown as DateConstructor;
  return () => { global.Date = OriginalDate; };
}
describe('formatRelativeTime', () => {
  const mockNow = new Date('2024-01-15T12:00:00Z').getTime();
  it('should return "just now" for 30 seconds ago', () => {
    const restore = mockDate(mockNow);
    const date = new Date(mockNow - 30 * 1000);
    expect(formatRelativeTime(date)).toBe('just now');
    restore();
  });
  it('should return "1 minute ago" for 1 minute ago', () => {
    const restore = mockDate(mockNow);
    const date = new Date(mockNow - 60 * 1000);
    expect(formatRelativeTime(date)).toBe('1 minute ago');
    restore();
  });
  it('should return "5 minutes ago" for 5 minutes ago', () => {
    const restore = mockDate(mockNow);
    const date = new Date(mockNow - 5 * 60 * 1000);
    expect(formatRelativeTime(date)).toBe('5 minutes ago');
    restore();
  });
  it('should return "1 hour ago" for 1 hour ago', () => {
    const restore = mockDate(mockNow);
    const date = new Date(mockNow - 60 * 60 * 1000);
    expect(formatRelativeTime(date)).toBe('1 hour ago');
    restore();
  });
  it('should return "5 hours ago" for 5 hours ago', () => {
    const restore = mockDate(mockNow);
    const date = new Date(mockNow - 5 * 60 * 60 * 1000);
    expect(formatRelativeTime(date)).toBe('5 hours ago');
    restore();
  });
  it('should return "1 day ago" for 1 day ago', () => {
    const restore = mockDate(mockNow);
    const date = new Date(mockNow - 24 * 60 * 60 * 1000);
    expect(formatRelativeTime(date)).toBe('1 day ago');
    restore();
  });
  it('should return "15 days ago" for 15 days ago', () => {
    const restore = mockDate(mockNow);
    const date = new Date(mockNow - 15 * 24 * 60 * 60 * 1000);
    expect(formatRelativeTime(date)).toBe('15 days ago');
    restore();
  });
  it('should return full date string for 31 days ago', () => {
    const restore = mockDate(mockNow);
    const date = new Date(mockNow - 31 * 24 * 60 * 60 * 1000);
    const result = formatRelativeTime(date);
    expect(result).toBe(date.toLocaleDateString());
    restore();
  });
  it('should support Date object input', () => {
    const restore = mockDate(mockNow);
    const date = new Date(mockNow - 60 * 1000);
    expect(formatRelativeTime(date)).toBe('1 minute ago');
    restore();
  });
  it('should support ISO string input', () => {
    const restore = mockDate(mockNow);
    const date = new Date(mockNow - 60 * 1000);
    expect(formatRelativeTime(date.toISOString())).toBe('1 minute ago');
    restore();
  });
});
