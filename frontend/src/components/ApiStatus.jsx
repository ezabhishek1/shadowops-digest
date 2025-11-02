import { useState, useEffect } from 'react';
import useDigest from '../hooks/useDigest';

const ApiStatus = () => {
  const { testConnection, apiBaseUrl } = useDigest();
  const [status, setStatus] = useState({ checking: true, connected: false, error: null });

  useEffect(() => {
    const checkConnection = async () => {
      setStatus({ checking: true, connected: false, error: null });
      
      const result = await testConnection();
      
      setStatus({
        checking: false,
        connected: result.success,
        error: result.success ? null : result.error
      });
    };

    // Check connection on mount
    checkConnection();

    // Set up periodic health checks every 30 seconds
    const interval = setInterval(checkConnection, 30000);

    return () => clearInterval(interval);
  }, [testConnection]);

  const handleRetryConnection = async () => {
    setStatus({ checking: true, connected: false, error: null });
    const result = await testConnection();
    setStatus({
      checking: false,
      connected: result.success,
      error: result.success ? null : result.error
    });
  };

  if (status.checking) {
    return (
      <div className="flex items-center space-x-2 text-sm text-gray-600">
        <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
        <span>Checking API connection...</span>
      </div>
    );
  }

  if (status.connected) {
    return (
      <div className="flex items-center space-x-2 text-sm text-green-600">
        <div className="w-2 h-2 bg-green-400 rounded-full"></div>
        <span>Connected to API ({apiBaseUrl})</span>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-2 text-sm">
      <div className="w-2 h-2 bg-red-400 rounded-full"></div>
      <span className="text-red-600">API connection failed</span>
      <button
        onClick={handleRetryConnection}
        className="text-blue-600 hover:text-blue-800 underline ml-2"
      >
        Retry
      </button>
      {status.error && (
        <div className="ml-2 text-xs text-gray-500">
          ({status.error})
        </div>
      )}
    </div>
  );
};

export default ApiStatus;