import { Component, createContext, useContext, useState, useEffect } from 'react';
import Home from './pages/Home';
import Layout from './components/Layout';
import './index.css';

// Global State Context for application-wide state management
const AppContext = createContext();

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
};

// Error Boundary Component for graceful error handling
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
    
    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error caught by boundary:', error, errorInfo);
    }
    
    // In production, you could send error to logging service
    // logErrorToService(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
            <div className="text-center">
              <div className="text-red-500 text-6xl mb-4">⚠️</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Something went wrong
              </h2>
              <p className="text-gray-600 mb-6">
                An unexpected error occurred. Please refresh the page to try again.
              </p>
              <button
                onClick={() => window.location.reload()}
                className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
              >
                Refresh Page
              </button>
            </div>
            {process.env.NODE_ENV === 'development' && (
              <details className="mt-6 text-sm">
                <summary className="cursor-pointer text-gray-500">
                  Error Details (Development)
                </summary>
                <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto">
                  {this.state.error && this.state.error.toString()}
                  <br />
                  {this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Theme Provider Component for global styling configuration
const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('default');

  useEffect(() => {
    // Load theme from localStorage or system preference
    const savedTheme = localStorage.getItem('shadowops-theme') || 'default';
    setTheme(savedTheme);
    
    // Apply theme class to document root
    document.documentElement.className = `theme-${savedTheme}`;
  }, []);

  // Theme update function for future use
  // const updateTheme = (newTheme) => {
  //   setTheme(newTheme);
  //   localStorage.setItem('shadowops-theme', newTheme);
  //   document.documentElement.className = `theme-${newTheme}`;
  // };

  return (
    <div className={`theme-${theme} min-h-screen transition-colors duration-200`}>
      {children}
    </div>
  );
};

// App Provider for comprehensive global state management
const AppProvider = ({ children }) => {
  const [globalState, setGlobalState] = useState({
    user: null,
    preferences: {
      theme: 'default',
      notifications: true,
      autoSave: true
    },
    app: {
      isLoading: false,
      error: null,
      lastAnalysis: null
    }
  });

  const updateGlobalState = (updates) => {
    setGlobalState(prev => ({ 
      ...prev, 
      ...updates 
    }));
  };

  const updatePreferences = (preferences) => {
    setGlobalState(prev => ({
      ...prev,
      preferences: { ...prev.preferences, ...preferences }
    }));
  };

  const setAppState = (appUpdates) => {
    setGlobalState(prev => ({
      ...prev,
      app: { ...prev.app, ...appUpdates }
    }));
  };

  const clearError = () => {
    setAppState({ error: null });
  };

  const value = {
    globalState,
    updateGlobalState,
    updatePreferences,
    setAppState,
    clearError
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

// Router Component with structure for future page additions
const Router = () => {
  const [currentPath, setCurrentPath] = useState(window.location.pathname);

  useEffect(() => {
    // Listen for browser navigation events
    const handlePopState = () => {
      setCurrentPath(window.location.pathname);
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  // Navigation helper function for future use
  const navigate = (path) => {
    window.history.pushState({}, '', path);
    setCurrentPath(path);
  };

  // Route configuration for easy expansion
  const routes = {
    '/': Home,
    '/home': Home,
    // Future routes can be added here:
    // '/analytics': AnalyticsPage,
    // '/settings': SettingsPage,
    // '/history': HistoryPage
  };

  const CurrentComponent = routes[currentPath] || routes['/'];
  
  return <CurrentComponent navigate={navigate} />;
};

// Main App Component
function App() {
  return (
    <ErrorBoundary>
      <AppProvider>
        <ThemeProvider>
          <Layout>
            <Router />
          </Layout>
        </ThemeProvider>
      </AppProvider>
    </ErrorBoundary>
  );
}

export default App;