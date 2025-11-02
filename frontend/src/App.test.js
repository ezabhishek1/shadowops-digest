import { render, screen } from '@testing-library/react';
import App from './App';

// Mock the Home component to avoid complex dependencies
jest.mock('./pages/Home', () => {
  return function MockHome() {
    return <div data-testid="home-page">Home Page</div>;
  };
});

describe('App Component', () => {
  test('renders without crashing', () => {
    render(<App />);
    expect(screen.getByTestId('home-page')).toBeInTheDocument();
  });

  test('renders ShadowOps Digest header', () => {
    render(<App />);
    expect(screen.getByText('ShadowOps Digest')).toBeInTheDocument();
  });

  test('renders app description', () => {
    render(<App />);
    expect(screen.getByText('AI-powered IT ticket analysis and insights')).toBeInTheDocument();
  });

  test('has proper theme class applied', () => {
    render(<App />);
    const themeElement = document.querySelector('.theme-default');
    expect(themeElement).toBeInTheDocument();
  });
});