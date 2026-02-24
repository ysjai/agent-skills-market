import { describe, it, expect, beforeEach, mock } from 'bun:test';
import { logout } from '../auth';
import '@testing-library/jest-dom';

const mockLogout = mock(() => Promise.resolve());

mock.module('../../lib/api', () => ({
  api: {
    logout: mockLogout,
  },
}));

describe('auth', () => {
  beforeEach(() => {
    mockLogout.mockClear();
  });

  describe('logout', () => {
    it('should call api.logout', async () => {
      mockLogout.mockResolvedValueOnce(undefined);

      await logout();

      expect(mockLogout).toHaveBeenCalled();
    });

    it('should complete successfully when api.logout resolves', async () => {
      mockLogout.mockResolvedValueOnce(undefined);

      await logout();

      expect(mockLogout).toHaveBeenCalledTimes(1);
    });
  });
});
