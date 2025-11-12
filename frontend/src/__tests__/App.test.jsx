import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../App';
import { MemoryRouter } from 'react-router-dom';

// Mock all route components
vi.mock('../pages/Chat', () => ({
  default: () => <div data-testid="chat-page">Chat Page</div>
}));

vi.mock('../pages/Extraction', () => ({
  default: () => <div data-testid="extraction-page">Extraction Page</div>
}));

vi.mock('../pages/Export', () => ({
  default: () => <div data-testid="export-page">Export Page</div>
}));

vi.mock('../pages/Query', () => ({
  default: () => <div data-testid="query-page">Query Page</div>
}));

vi.mock('../pages/UseCaseDetail', () => ({
  default: () => <div data-testid="use-case-detail-page">Use Case Detail Page</div>
}));

vi.mock('../pages/UseCaseRefine', () => ({
  default: () => <div data-testid="use-case-refine-page">Use Case Refine Page</div>
}));

// Mock layout components
vi.mock('../components/Layout/Sidebar', () => ({
  default: () => <div data-testid="sidebar">Sidebar</div>
}));

vi.mock('../components/Layout/Header', () => ({
  default: () => <div data-testid="header">Header</div>
}));

describe('App Component', () => {
  const renderWithRouter = (initialRoute = '/') => {
    return render(
      <MemoryRouter initialEntries={[initialRoute]}>
        <App />
      </MemoryRouter>
    );
  };

  it('renders layout components', () => {
    renderWithRouter();
    expect(screen.getByTestId('sidebar')).toBeInTheDocument();
    expect(screen.getByTestId('header')).toBeInTheDocument();
  });

  it('renders chat page on root route', () => {
    renderWithRouter('/');
    expect(screen.getByTestId('chat-page')).toBeInTheDocument();
  });

  it('renders extraction page on /extraction route', () => {
    renderWithRouter('/extraction');
    expect(screen.getByTestId('extraction-page')).toBeInTheDocument();
  });

  it('renders export page on /export route', () => {
    renderWithRouter('/export');
    expect(screen.getByTestId('export-page')).toBeInTheDocument();
  });

  it('redirects to home when accessing removed analytics route', () => {
    renderWithRouter('/analytics');
    expect(screen.getByTestId('chat-page')).toBeInTheDocument();
  });

  it('renders query page on /query route', () => {
    renderWithRouter('/query');
    expect(screen.getByTestId('query-page')).toBeInTheDocument();
  });

  it('renders use case detail page on /use-case/:id route', () => {
    renderWithRouter('/use-case/123');
    expect(screen.getByTestId('use-case-detail-page')).toBeInTheDocument();
  });

  it('renders use case refine page on /use-case/:id/refine route', () => {
    renderWithRouter('/use-case/123/refine');
    expect(screen.getByTestId('use-case-refine-page')).toBeInTheDocument();
  });
});