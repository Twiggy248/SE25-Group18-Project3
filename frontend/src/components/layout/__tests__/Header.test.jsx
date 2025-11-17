import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Header from '../Header';

describe('Header Component', () => {
  const renderWithRouter = () => {
    return render(
      <BrowserRouter>
        <Header />
      </BrowserRouter>
    );
  };

  it('renders the header', () => {
    renderWithRouter();
    const logoElement = screen.getByAltText('ReqEngine');
    expect(logoElement).toBeInTheDocument();
  });

  it('links to home page', () => {
    renderWithRouter();
    const homeLink = screen.getByRole('link');
    expect(homeLink).toHaveAttribute('href', '/');
  });

  it('renders logo with correct styles', () => {
    renderWithRouter();
    const logoElement = screen.getByAltText('ReqEngine');
    expect(logoElement).toHaveClass('h-full');
    expect(logoElement).toHaveClass('object-cover');
    expect(logoElement).toHaveClass('object-left');
  });
});