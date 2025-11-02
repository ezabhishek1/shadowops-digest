import { useState } from 'react';
import useDigest from '../hooks/useDigest';
import DigestCard from '../components/DigestCard';

const Home = () => {
  const [tickets, setTickets] = useState('');
  const [avgTime, setAvgTime] = useState(30);
  const [hourlyCost, setHourlyCost] = useState(40.0);
  const [validationErrors, setValidationErrors] = useState({});
  const { data, loading, error, generateDigest } = useDigest();

  const validateForm = () => {
    const errors = {};
    
    // Parse tickets from textarea (one per line)
    const ticketList = tickets
      .split('\n')
      .map(ticket => ticket.trim())
      .filter(ticket => ticket.length > 0);

    // Validate tickets
    if (ticketList.length === 0) {
      errors.tickets = 'Please enter at least one ticket description';
    } else if (ticketList.length > 1000) {
      errors.tickets = 'Maximum 1000 tickets allowed';
    }

    // Validate average time
    const avgTimeNum = parseInt(avgTime);
    if (!avgTimeNum || avgTimeNum < 1 || avgTimeNum > 480) {
      errors.avgTime = 'Average time must be between 1 and 480 minutes';
    }

    // Validate hourly cost
    const hourlyCostNum = parseFloat(hourlyCost);
    if (!hourlyCostNum || hourlyCostNum < 1.00 || hourlyCostNum > 500.00) {
      errors.hourlyCost = 'Hourly cost must be between $1.00 and $500.00';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    // Parse tickets from textarea (one per line)
    const ticketList = tickets
      .split('\n')
      .map(ticket => ticket.trim())
      .filter(ticket => ticket.length > 0);

    const requestData = {
      tickets: ticketList,
      avg_time_per_ticket_minutes: parseInt(avgTime),
      hourly_cost_usd: parseFloat(hourlyCost)
    };

    await generateDigest(requestData);
  };

  const handleRetry = () => {
    handleSubmit({ preventDefault: () => {} });
  };

  const clearValidationError = (field) => {
    if (validationErrors[field]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="px-4 sm:px-6 lg:px-8">

        {/* Input Form */}
        <div className="bg-white rounded-lg shadow-md p-4 sm:p-6 mb-8">
          <h2 className="text-xl sm:text-2xl font-semibold text-gray-800 mb-6">
            Ticket Analysis Input
          </h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Tickets Input */}
            <div>
              <label htmlFor="tickets" className="block text-sm font-medium text-gray-700 mb-2">
                Ticket Descriptions (one per line) *
              </label>
              <textarea
                id="tickets"
                value={tickets}
                onChange={(e) => {
                  setTickets(e.target.value);
                  clearValidationError('tickets');
                }}
                placeholder="Enter ticket descriptions, one per line...&#10;Example:&#10;VPN connection fails on Windows 10&#10;Outlook password reset needed&#10;Printer not responding in Building A"
                className={`w-full h-32 sm:h-40 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y ${
                  validationErrors.tickets 
                    ? 'border-red-300 bg-red-50' 
                    : 'border-gray-300'
                }`}
                required
              />
              {validationErrors.tickets && (
                <p className="mt-1 text-sm text-red-600">{validationErrors.tickets}</p>
              )}
              <p className="mt-1 text-xs text-gray-500">
                Enter 1-1000 ticket descriptions, one per line
              </p>
            </div>

            {/* Parameter Inputs */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
              <div>
                <label htmlFor="avgTime" className="block text-sm font-medium text-gray-700 mb-2">
                  Average Time per Ticket (minutes) *
                </label>
                <input
                  type="number"
                  id="avgTime"
                  value={avgTime}
                  onChange={(e) => {
                    setAvgTime(e.target.value);
                    clearValidationError('avgTime');
                  }}
                  min="1"
                  max="480"
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    validationErrors.avgTime 
                      ? 'border-red-300 bg-red-50' 
                      : 'border-gray-300'
                  }`}
                  required
                />
                {validationErrors.avgTime && (
                  <p className="mt-1 text-sm text-red-600">{validationErrors.avgTime}</p>
                )}
                <p className="mt-1 text-xs text-gray-500">
                  Range: 1-480 minutes
                </p>
              </div>

              <div>
                <label htmlFor="hourlyCost" className="block text-sm font-medium text-gray-700 mb-2">
                  Hourly Cost (USD) *
                </label>
                <input
                  type="number"
                  id="hourlyCost"
                  value={hourlyCost}
                  onChange={(e) => {
                    setHourlyCost(e.target.value);
                    clearValidationError('hourlyCost');
                  }}
                  min="1.00"
                  max="500.00"
                  step="0.01"
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    validationErrors.hourlyCost 
                      ? 'border-red-300 bg-red-50' 
                      : 'border-gray-300'
                  }`}
                  required
                />
                {validationErrors.hourlyCost && (
                  <p className="mt-1 text-sm text-red-600">{validationErrors.hourlyCost}</p>
                )}
                <p className="mt-1 text-xs text-gray-500">
                  Range: $1.00-$500.00
                </p>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Generating Digest...
                </div>
              ) : (
                'Generate Digest'
              )}
            </button>
          </form>

          {/* Error Display with Retry */}
          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3 flex-1">
                  <h3 className="text-sm font-medium text-red-800">
                    Analysis Failed
                  </h3>
                  <p className="mt-1 text-sm text-red-700">{error}</p>
                  <div className="mt-3">
                    <button
                      onClick={handleRetry}
                      disabled={loading}
                      className="bg-red-100 text-red-800 px-3 py-1 rounded-md text-sm font-medium hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 transition-colors"
                    >
                      Try Again
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Results Display */}
        {data && <DigestCard data={data} />}
      </div>
    </div>
  );
};

export default Home;