import { render, RenderOptions } from '@testing-library/react';
import React, { ReactElement } from 'react';

export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  return render(ui, {
    wrapper: ({ children }) => <>{children}</>,
    ...options,
  });
}

export * from '@testing-library/react';
