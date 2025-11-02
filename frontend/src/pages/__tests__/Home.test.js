import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Home from '../Home';

// Mock the useDigest hook
const mockGenerateDigest = jest.fn();
const mockData = null;
const mockLoading = false;
const mockError = null;

jest.mock('../../hooks/useDigest', () => ({
  __esModule: true,
  default: () => ({
    data: mockData,
    loading: mockLoading,
    error: mockError,
    generateDigest: mockGenerateDigest
  })
}));

// Mock DigestCard component
jest.mock('../../components/DigestCard', () => {
  return function MockDigestCard({ data }) {
    return <div data-testid="digest-card">Digest Card: {JSON.stringify(data)}</div>;
  };
});

describe('Home Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders form with all input fields', () => {
    render(<Home />);

    expect(screen.getByLabelText(/ticket descriptions/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/average time per ticket/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/hourly cost/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /generate digest/i })).toBeInTheDocument();
  });

  test('renders with default values', () => {
    render(<Home />);

    const avgTimeInput = screen.getByLabelText(/average time per ticket/i);
    const hourlyCostInput = screen.getByLabelText(/hourly cost/i);

    expect(avgTimeInput).toHaveValue(30);
    expect(hourlyCostInput).toHaveValue(40);
  });

  test('updates ticket textarea on user input', async () => {
    const user = userEvent.setup();
    render(<Home />);

    const ticketInput = screen.getByLabelText(/ticket descriptions/i);
    await user.type(ticketInput, 'Test ticket 1\nTest ticket 2');

    expect(ticketInput).toHaveValue('Test ticket 1\nTest ticket 2');
  });

  test('updates average time on user input', async () => {
    const user = userEvent.setup();
    render(<Home />);

    const avgTimeInput = screen.getByLabelText(/average time per ticket/i);
    await user.clear(avgTimeInput);
    await user.type(avgTimeInput, '45');

    expect(avgTimeInput).toHaveValue(45);
  });

  test('updates hourly cost on user input', async () => {
    const user = userEvent.setup();
    render(<Home />);

    const hourlyCostInput = screen.getByLabelText(/hourly cost/i);
    await user.clear(hourlyCostInput);
    await user.type(hourlyCostInput, '50.00');

    expect(hourlyCostInput).toHaveValue(50);
  });

  test('shows validation error for empty tickets', async () => {
    const user = userEvent.setup();
    render(<Home />);

    const submitButton = screen.getByRole('button', { name: /generate digest/i });
    await user.click(submitButton);

    expect(screen.getByText(/please enter at least one ticket description/i)).toBeInTheDocument();
    expect(mockGenerateDigest).not.toHaveBeenCalled();
  });

  test('shows validation error for too many tickets', async () => {
    const user = userEvent.setup();
    render(<Home />);

    const ticketInput = screen.getByLabelText(/ticket descriptions/i);
    const manyTickets = Array(1001).fill('Test ticket').join('\n');
    await user.type(ticketInput, manyTickets);

    const submitButton = screen.getByRole('button', { name: /generate digest/i });
    await user.click(submitButton);

    expect(screen.getByText(/maximum 1000 tickets allowed/i)).toBeInTheDocument();
    expect(mockGenerateDigest).not.toHaveBeenCalled();
  });

  test('shows validation error for invalid average time (too low)', async () => {
    const user = userEvent.setup();
    render(<Home />);

    const ticketInput = screen.getByLabelText(/ticket descriptions/i);
    await user.type(ticketInput, 'Test ticket');

    const avgTimeInput = screen.getByLabelText(/average time per ticket/i);
    await user.clear(avgTimeInput);
    await user.type(avgTimeInput, '0');

    const submitButton = screen.getByRole('button', { name: /generate digest/i });
    await user.click(submitButton);

    expect(screen.getByText(/average time must be between 1 and 480 minutes/i)).toBeInTheDocument();
    expect(mockGenerateDigest).not.toHaveBeenCalled();
  });

  test('shows validation error for invalid average time (too high)', async () => {
    const user = userEvent.setup();
    render(<Home />);

    const ticketInput = screen.getByLabelText(/ticket descriptions/i);
    await user.type(ticketInput, 'Test ticket');

    const avgTimeInput = screen.getByLabelText(/average time per ticket/i);
    await user.clear(avgTimeInput);
    await user.type(avgTimeInput, '500');

    const submitButton = screen.getByRole('button', { name: /generate digest/i });
    await user.click(submitButton);

    expect(screen.getByText(/average time must be between 1 and 480 minutes/i)).toBeInTheDocument();
    expect(mockGenerateDigest).not.toHaveBeenCalled();
  });

  test('shows validation error for invalid hourly cost (too low)', async () => {
    const user = userEvent.setup();
    render(<Home />);

    const ticketInput = screen.getByLabelText(/ticket descriptions/i);
    await user.type(ticketInput, 'Test ticket');

    const hourlyCostInput = screen.getByLabelText(/hourly cost/i);
    await user.clear(hourlyCostInput);
    await user.type(hourlyCostInput, '0.50');

    const submitButton = screen.getByRole('button', { name: /generate digest/i });
    await user.click(submitButton);

    expect(screen.getByText(/hourly cost must be between \$1\.00 and \$500\.00/i)).toBeInTheDocument();
    expect(mockGenerateDigest).not.toHaveBeenCalled();
  });

  test('shows validation error for invalid hourly cost (too high)', async () => {
    const user = userEvent.setup();
    render(<Home />);

    const ticketInput = screen.getByLabelText(/ticket descriptions/i);
    await user.type(ticketInput, 'Test ticket');

    const hourlyCostInput = screen.getByLabelText(/hourly cost/i);
    await user.clear(hourlyCostInput);
    await user.type(hourlyCostInput, '600');

    const submitButton = screen.getByRole('button', { name: /generate digest/i });
    await user.click(submitButton);

    expect(screen.getByText(/hourly cost must be between \$1\.00 and \$500\.00/i)).toBeInTheDocument();
    expect(mockGenerateDigest).not.toHaveBeenCalled();
  });

  test('clears validation error when user corrects input', async () => {
    const user = userEvent.setup();
    render(<Home />);

    // Submit with empty tickets to trigger error
    const submitButton = screen.getByRole('button', { name: /generate digest/i });
    await user.click(submitButton);

    expect(screen.getByText(/please enter at least one ticket description/i)).toBeInTheDocument();

    // Now type in tickets
    const ticketInput = screen.getByLabelText(/ticket descriptions/i);
    await user.type(ticketInput, 'Test ticket');

    // Error should be cleared
    expect(screen.queryByText(/please enter at least one ticket description/i)).not.toBeInTheDocument();
  });

  test('submits form with valid data', async () => {
    const user = userEvent.setup();
    mockGenerateDigest.mockResolvedValue();

    render(<Home />);

    const ticketInput = screen.getByLabelText(/ticket descriptions/i);
    await user.type(ticketInput, 'Test ticket 1\nTest ticket 2\nTest ticket 3');

    const avgTimeInput = screen.getByLabelText(/average time per ticket/i);
    await user.clear(avgTimeInput);
    await user.type(avgTimeInput, '45');

    const hourlyCostInput = screen.getByLabelText(/hourly cost/i);
    await user.clear(hourlyCostInput);
    await user.type(hourlyCostInput, '50.00');

    const submitButton = screen.getByRole('button', { name: /generate digest/i });
    await user.click(submitButton);

    expect(mockGenerateDigest).toHaveBeenCalledWith({
      tickets: ['Test ticket 1', 'Test ticket 2', 'Test ticket 3'],
      avg_time_per_ticket_minutes: 45,
      hourly_cost_usd: 50.00
    });
  });

  test('filters out empty lines from tickets', async () => {
    const user = userEvent.setup();
    mockGenerateDigest.mockResolvedValue();

    render(<Home />);

    const ticketInput = screen.getByLabelText(/ticket descriptions/i);
    await user.type(ticketInput, 'Test ticket 1\n\n\nTest ticket 2\n  \nTest ticket 3');

    const submitButton = screen.getByRole('button', { name: /generate digest/i });
    await user.click(submitButton);

    expect(mockGenerateDigest).toHaveBeenCalledWith({
      tickets: ['Test ticket 1', 'Test ticket 2', 'Test ticket 3'],
      avg_time_per_ticket_minutes: 30,
      hourly_cost_usd: 40.00
    });
  });

  test('trims whitespace from ticket descriptions', async () => {
    const user = userEvent.setup();
    mockGenerateDigest.mockResolvedValue();

    render(<Home />);

    const ticketInput = screen.getByLabelText(/ticket descriptions/i);
    await user.type(ticketInput, '  Test ticket 1  \n  Test ticket 2  ');

    const submitButton = screen.getByRole('button', { name: /generate digest/i });
    await user.click(submitButton);

    expect(mockGenerateDigest).toHaveBeenCalledWith({
      tickets: ['Test ticket 1', 'Test ticket 2'],
      avg_time_per_ticket_minutes: 30,
      hourly_cost_usd: 40.00
    });
  });

  test('displays helper text for input fields', () => {
    render(<Home />);

    expect(screen.getByText(/enter 1-1000 ticket descriptions/i)).toBeInTheDocument();
    expect(screen.getByText(/range: 1-480 minutes/i)).toBeInTheDocument();
    expect(screen.getByText(/range: \$1\.00-\$500\.00/i)).toBeInTheDocument();
  });

  test('applies error styling to invalid fields', async () => {
    const user = userEvent.setup();
    render(<Home />);

    const submitButton = screen.getByRole('button', { name: /generate digest/i });
    await user.click(submitButton);

    const ticketInput = screen.getByLabelText(/ticket descriptions/i);
    expect(ticketInput).toHaveClass('border-red-300', 'bg-red-50');
  });

  test('removes error styling when field becomes valid', async () => {
    const user = userEvent.setup();
    render(<Home />);

    // Trigger error
    const submitButton = screen.getByRole('button', { name: /generate digest/i });
    await user.click(submitButton);

    const ticketInput = screen.getByLabelText(/ticket descriptions/i);
    expect(ticketInput).toHaveClass('border-red-300', 'bg-red-50');

    // Fix the error
    await user.type(ticketInput, 'Test ticket');

    expect(ticketInput).not.toHaveClass('border-red-300', 'bg-red-50');
    expect(ticketInput).toHaveClass('border-gray-300');
  });

  test('has proper form accessibility attributes', () => {
    render(<Home />);

    const ticketInput = screen.getByLabelText(/ticket descriptions/i);
    const avgTimeInput = screen.getByLabelText(/average time per ticket/i);
    const hourlyCostInput = screen.getByLabelText(/hourly cost/i);

    expect(ticketInput).toHaveAttribute('required');
    expect(avgTimeInput).toHaveAttribute('required');
    expect(hourlyCostInput).toHaveAttribute('required');

    expect(avgTimeInput).toHaveAttribute('min', '1');
    expect(avgTimeInput).toHaveAttribute('max', '480');

    expect(hourlyCostInput).toHaveAttribute('min', '1.00');
    expect(hourlyCostInput).toHaveAttribute('max', '500.00');
    expect(hourlyCostInput).toHaveAttribute('step', '0.01');
  });

  test('has proper heading structure', () => {
    render(<Home />);

    const heading = screen.getByRole('heading', { level: 2 });
    expect(heading).toHaveTextContent('Ticket Analysis Input');
  });
});
