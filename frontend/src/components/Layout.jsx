import ApiStatus from './ApiStatus';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            ShadowOps Digest
          </h1>
          <p className="text-lg text-gray-600">
            AI-powered IT ticket analysis and insights
          </p>
          <div className="mt-4 flex justify-center">
            <ApiStatus />
          </div>
        </header>
        
        <main>
          {children}
        </main>
        
        <footer className="mt-12 text-center text-gray-500 text-sm">
          <p>&copy; 2024 ShadowOps Digest. Built for IT operations optimization.</p>
        </footer>
      </div>
    </div>
  );
};

export default Layout;