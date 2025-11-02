
const DigestCard = ({ data }) => {
  if (!data) return null;

  const { clusters, suggestion, time_wasted_hours, cost_saved_usd, digest_summary } = data;

  // Color palette for different clusters
  const clusterColors = [
    { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-800', badge: 'bg-blue-100' },
    { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-800', badge: 'bg-purple-100' },
    { bg: 'bg-indigo-50', border: 'border-indigo-200', text: 'text-indigo-800', badge: 'bg-indigo-100' },
    { bg: 'bg-pink-50', border: 'border-pink-200', text: 'text-pink-800', badge: 'bg-pink-100' },
    { bg: 'bg-cyan-50', border: 'border-cyan-200', text: 'text-cyan-800', badge: 'bg-cyan-100' },
  ];

  // Get the largest cluster for highlighting
  const clusterEntries = Object.entries(clusters);
  const largestCluster = clusterEntries.reduce((max, current) => 
    current[1].length > max[1].length ? current : max
  );

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          📊 Analysis Results
        </h2>
        <p className="text-gray-600">
          AI-powered insights from your support tickets
        </p>
      </div>

      {/* Executive Summary Card */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6 shadow-sm">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-blue-600 text-lg">📋</span>
            </div>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">Executive Summary</h3>
            <p className="text-blue-800 leading-relaxed">{digest_summary}</p>
          </div>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {/* Time Wasted Card */}
        <div className="bg-gradient-to-br from-red-50 to-orange-50 border border-red-200 rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
              <span className="text-red-600 text-xl">⏰</span>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-red-700 uppercase tracking-wide">Time Wasted</p>
              <p className="text-3xl font-bold text-red-800">{time_wasted_hours}</p>
              <p className="text-sm text-red-600">hours</p>
            </div>
          </div>
          <div className="w-full bg-red-200 rounded-full h-2">
            <div className="bg-red-500 h-2 rounded-full" style={{ width: '75%' }}></div>
          </div>
        </div>

        {/* Cost Savings Card */}
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <span className="text-green-600 text-xl">💰</span>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-green-700 uppercase tracking-wide">Potential Savings</p>
              <p className="text-3xl font-bold text-green-800">${cost_saved_usd}</p>
              <p className="text-sm text-green-600">USD</p>
            </div>
          </div>
          <div className="w-full bg-green-200 rounded-full h-2">
            <div className="bg-green-500 h-2 rounded-full" style={{ width: '85%' }}></div>
          </div>
        </div>
      </div>

      {/* Improvement Suggestion Card - Highlighted */}
      <div className="bg-gradient-to-r from-yellow-50 via-amber-50 to-orange-50 border-2 border-yellow-300 rounded-xl p-6 shadow-lg relative overflow-hidden">
        {/* Highlight decoration */}
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-yellow-400 to-orange-400"></div>
        
        <div className="flex items-start space-x-4">
          <div className="flex-shrink-0">
            <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center border-2 border-yellow-300">
              <span className="text-yellow-600 text-2xl">💡</span>
            </div>
          </div>
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-3">
              <h3 className="text-xl font-bold text-yellow-900">Top Improvement Suggestion</h3>
              <span className="bg-yellow-200 text-yellow-800 text-xs font-semibold px-2 py-1 rounded-full">
                HIGH IMPACT
              </span>
            </div>
            <p className="text-yellow-800 text-lg leading-relaxed font-medium">{suggestion}</p>
            <div className="mt-4 flex items-center text-sm text-yellow-700">
              <span className="mr-2">🎯</span>
              <span>Targets the largest cluster: <strong>{largestCluster[0]}</strong> ({largestCluster[1].length} tickets)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Ticket Clusters */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-semibold text-gray-900">Ticket Clusters</h3>
            <span className="bg-gray-100 text-gray-700 text-sm font-medium px-3 py-1 rounded-full">
              {clusterEntries.length} cluster{clusterEntries.length !== 1 ? 's' : ''}
            </span>
          </div>
        </div>
        
        <div className="p-6 space-y-6">
          {clusterEntries.map(([clusterName, ticketIndices], index) => {
            const colorScheme = clusterColors[index % clusterColors.length];
            const isLargestCluster = clusterName === largestCluster[0];
            
            return (
              <div 
                key={index} 
                className={`${colorScheme.bg} ${colorScheme.border} border rounded-xl p-5 transition-all duration-200 hover:shadow-md ${
                  isLargestCluster ? 'ring-2 ring-yellow-300 ring-opacity-50' : ''
                }`}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 ${colorScheme.badge} rounded-full flex items-center justify-center`}>
                      <span className={`${colorScheme.text} font-bold text-sm`}>
                        {index + 1}
                      </span>
                    </div>
                    <h4 className={`font-semibold ${colorScheme.text} text-lg`}>
                      {clusterName}
                    </h4>
                    {isLargestCluster && (
                      <span className="bg-yellow-200 text-yellow-800 text-xs font-bold px-2 py-1 rounded-full">
                        LARGEST
                      </span>
                    )}
                  </div>
                  <div className="text-right">
                    <p className={`text-sm font-medium ${colorScheme.text} opacity-75`}>
                      {ticketIndices.length} ticket{ticketIndices.length !== 1 ? 's' : ''}
                    </p>
                    <p className={`text-xs ${colorScheme.text} opacity-60`}>
                      {((ticketIndices.length / Object.values(clusters).flat().length) * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
                
                {/* Ticket indices with improved visual representation */}
                <div className="flex flex-wrap gap-2 mb-3">
                  {ticketIndices.map((ticketIndex) => (
                    <span
                      key={ticketIndex}
                      className={`inline-flex items-center px-3 py-1 ${colorScheme.badge} ${colorScheme.text} text-sm font-medium rounded-full border ${colorScheme.border} hover:shadow-sm transition-shadow`}
                    >
                      <span className="mr-1">#</span>
                      {ticketIndex + 1}
                    </span>
                  ))}
                </div>
                
                {/* Progress bar showing cluster size relative to total */}
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`${colorScheme.bg.replace('50', '400')} h-2 rounded-full transition-all duration-300`}
                    style={{ 
                      width: `${(ticketIndices.length / Object.values(clusters).flat().length) * 100}%` 
                    }}
                  ></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default DigestCard;