import { render, screen } from '@testing-library/react';
import DigestCard from '../DigestCard';

describe('DigestCard Component', () => {
  const mockData = {
    clusters: {
      'Network Issues': [0, 2, 4],
      'Authentication Problems': [1, 3],
      'Hardware Failures': [5]
    },
    suggestion: 'Create a network troubleshooting guide for common connectivity issues',
    time_wasted_hours: 4.5,
    cost_saved_usd: 180.0,
    digest_summary: '6 tickets clustered into 3 categories. Primary issue: Network Issues (3 tickets). Recommendation: Create network guide. Potential savings: 4.5 hours, $180.'
  };

  test('renders nothing when no data provided', () => {
    const { container } = render(<DigestCard data={null} />);
    expect(container.firstChild).toBeNull();
  });

  test('renders all main sections with data', () => {
    render(<DigestCard data={mockData} />);

    expect(screen.getByText('📊 Analysis Results')).toBeInTheDocument();
    expect(screen.getByText('Executive Summary')).toBeInTheDocument();
    expect(screen.getByText('Time Wasted')).toBeInTheDocument();
    expect(screen.getByText('Potential Savings')).toBeInTheDocument();
    expect(screen.getByText('Top Improvement Suggestion')).toBeInTheDocument();
    expect(screen.getByText('Ticket Clusters')).toBeInTheDocument();
  });

  test('displays executive summary correctly', () => {
    render(<DigestCard data={mockData} />);

    expect(screen.getByText(mockData.digest_summary)).toBeInTheDocument();
  });

  test('displays time wasted metrics', () => {
    render(<DigestCard data={mockData} />);

    expect(screen.getByText('4.5')).toBeInTheDocument();
    expect(screen.getByText('hours')).toBeInTheDocument();
  });

  test('displays cost savings metrics', () => {
    render(<DigestCard data={mockData} />);

    expect(screen.getByText('$180')).toBeInTheDocument();
    expect(screen.getByText('USD')).toBeInTheDocument();
  });

  test('displays improvement suggestion', () => {
    render(<DigestCard data={mockData} />);

    expect(screen.getByText(mockData.suggestion)).toBeInTheDocument();
    expect(screen.getByText('HIGH IMPACT')).toBeInTheDocument();
  });

  test('displays correct number of clusters', () => {
    render(<DigestCard data={mockData} />);

    expect(screen.getByText('3 clusters')).toBeInTheDocument();
  });

  test('displays all cluster names and ticket counts', () => {
    render(<DigestCard data={mockData} />);

    // Check cluster names
    expect(screen.getByText('Network Issues')).toBeInTheDocument();
    expect(screen.getByText('Authentication Problems')).toBeInTheDocument();
    expect(screen.getByText('Hardware Failures')).toBeInTheDocument();

    // Check ticket counts
    expect(screen.getByText('3 tickets')).toBeInTheDocument();
    expect(screen.getByText('2 tickets')).toBeInTheDocument();
    expect(screen.getByText('1 ticket')).toBeInTheDocument();
  });

  test('displays ticket indices correctly', () => {
    render(<DigestCard data={mockData} />);

    // Network Issues cluster should show tickets #1, #3, #5 (indices 0, 2, 4 + 1)
    expect(screen.getByText('#1')).toBeInTheDocument();
    expect(screen.getByText('#3')).toBeInTheDocument();
    expect(screen.getByText('#5')).toBeInTheDocument();

    // Authentication Problems cluster should show tickets #2, #4 (indices 1, 3 + 1)
    expect(screen.getByText('#2')).toBeInTheDocument();
    expect(screen.getByText('#4')).toBeInTheDocument();

    // Hardware Failures cluster should show ticket #6 (index 5 + 1)
    expect(screen.getByText('#6')).toBeInTheDocument();
  });

  test('identifies and highlights largest cluster', () => {
    render(<DigestCard data={mockData} />);

    // Network Issues has 3 tickets, should be marked as largest
    expect(screen.getByText('LARGEST')).toBeInTheDocument();
  });

  test('calculates cluster percentages correctly', () => {
    render(<DigestCard data={mockData} />);

    // Network Issues: 3/6 = 50%
    expect(screen.getByText('50.0%')).toBeInTheDocument();
    
    // Authentication Problems: 2/6 = 33.3%
    expect(screen.getByText('33.3%')).toBeInTheDocument();
    
    // Hardware Failures: 1/6 = 16.7%
    expect(screen.getByText('16.7%')).toBeInTheDocument();
  });

  test('shows target cluster information in suggestion section', () => {
    render(<DigestCard data={mockData} />);

    expect(screen.getByText(/targets the largest cluster/i)).toBeInTheDocument();
    expect(screen.getByText(/network issues/i)).toBeInTheDocument();
    expect(screen.getByText('(3 tickets)')).toBeInTheDocument();
  });

  test('handles single cluster correctly', () => {
    const singleClusterData = {
      ...mockData,
      clusters: {
        'Single Issue': [0, 1, 2, 3, 4, 5]
      }
    };

    render(<DigestCard data={singleClusterData} />);

    expect(screen.getByText('1 cluster')).toBeInTheDocument();
    expect(screen.getByText('6 tickets')).toBeInTheDocument();
    expect(screen.getByText('100.0%')).toBeInTheDocument();
  });

  test('handles empty clusters gracefully', () => {
    const emptyClusterData = {
      ...mockData,
      clusters: {}
    };

    render(<DigestCard data={emptyClusterData} />);

    expect(screen.getByText('0 clusters')).toBeInTheDocument();
  });

  test('displays proper accessibility attributes', () => {
    render(<DigestCard data={mockData} />);

    // Check for proper heading structure
    const mainHeading = screen.getByRole('heading', { level: 2 });
    expect(mainHeading).toHaveTextContent('📊 Analysis Results');

    const summaryHeading = screen.getByRole('heading', { level: 3, name: /executive summary/i });
    expect(summaryHeading).toBeInTheDocument();
  });

  test('uses proper semantic HTML structure', () => {
    const { container } = render(<DigestCard data={mockData} />);

    // Should have proper div structure with classes
    const mainContainer = container.querySelector('.max-w-4xl');
    expect(mainContainer).toBeInTheDocument();

    // Should have cards with proper styling
    const cards = container.querySelectorAll('.rounded-xl');
    expect(cards.length).toBeGreaterThan(0);
  });

  test('handles very long suggestion text', () => {
    const longSuggestionData = {
      ...mockData,
      suggestion: 'This is a very long suggestion that should be displayed properly even when it contains a lot of text and might wrap to multiple lines in the user interface'
    };

    render(<DigestCard data={longSuggestionData} />);

    expect(screen.getByText(longSuggestionData.suggestion)).toBeInTheDocument();
  });

  test('handles cluster names with special characters', () => {
    const specialCharacterData = {
      ...mockData,
      clusters: {
        'Network & Connectivity Issues': [0, 1],
        'Authentication/Authorization Problems': [2, 3],
        'Hardware (Physical) Failures': [4, 5]
      }
    };

    render(<DigestCard data={specialCharacterData} />);

    expect(screen.getByText('Network & Connectivity Issues')).toBeInTheDocument();
    expect(screen.getByText('Authentication/Authorization Problems')).toBeInTheDocument();
    expect(screen.getByText('Hardware (Physical) Failures')).toBeInTheDocument();
  });

  test('displays correct visual indicators and icons', () => {
    render(<DigestCard data={mockData} />);

    // Check for emoji icons in the text content
    expect(screen.getByText(/📊/)).toBeInTheDocument(); // Analysis Results
    expect(screen.getByText(/📋/)).toBeInTheDocument(); // Executive Summary
    expect(screen.getByText(/⏰/)).toBeInTheDocument(); // Time Wasted
    expect(screen.getByText(/💰/)).toBeInTheDocument(); // Potential Savings
    expect(screen.getByText(/💡/)).toBeInTheDocument(); // Suggestion
    expect(screen.getByText(/🎯/)).toBeInTheDocument(); // Target cluster
  });
});