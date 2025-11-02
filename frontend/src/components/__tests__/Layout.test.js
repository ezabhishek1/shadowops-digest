import React from 'react';
import { render, screen } from '@testing-library/react';
import Layout from '../Layout';

// Mock ApiStatus component
jest.mock('../ApiStatus', () => {
  return function MockApiStatus() {
    return <div data-testid="api-status">API Status</div>;
  };
});

describe('Layout Component', () => {
  test('renders header with title and description', () => {
    render(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    expect(screen.getByText('ShadowOps Digest')).toBeInTheDocument();
    expect(screen.getByText('AI-powered IT ticket analysis and insights')).toBeInTheDocument();
  });

  test('renders children content', () => {
    render(
      <Layout>
        <div data-testid="test-child">Test Content</div>
      </Layout>
    );

    expect(screen.getByTestId('test-child')).toBeInTheDocument();
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  test('renders ApiStatus component', () => {
    render(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    expect(screen.getByTestId('api-status')).toBeInTheDocument();
  });

  test('renders footer with copyright', () => {
    render(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    expect(screen.getByText(/© 2024 ShadowOps Digest/i)).toBeInTheDocument();
    expect(screen.getByText(/Built for IT operations optimization/i)).toBeInTheDocument();
  });

  test('applies correct CSS classes for layout structure', () => {
    const { container } = render(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    const mainContainer = container.firstChild;
    expect(mainContainer).toHaveClass('min-h-screen', 'bg-gray-50');
  });

  test('header has proper text styling', () => {
    render(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    const title = screen.getByText('ShadowOps Digest');
    expect(title).toHaveClass('text-4xl', 'font-bold', 'text-gray-900');
  });

  test('renders main content area', () => {
    const { container } = render(
      <Layout>
        <div data-testid="main-content">Main Content</div>
      </Layout>
    );

    const mainElement = container.querySelector('main');
    expect(mainElement).toBeInTheDocument();
    expect(mainElement).toContainElement(screen.getByTestId('main-content'));
  });
});
