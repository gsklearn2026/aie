import React from 'react';
import { AlertTriangle, RefreshCw, Wifi } from 'lucide-react';

const ErrorDisplay = ({ 
  error, 
  onRetry, 
  showRetry = true,
  title = "Something went wrong"
}) => {
  const getErrorIcon = (errorCode) => {
    if (errorCode?.includes('NETWORK') || errorCode?.includes('TIMEOUT')) {
      return <Wifi className="error-icon network" size={48} />;
    }
    return <AlertTriangle className="error-icon" size={48} />;
  };

  const getErrorMessage = (error) => {
    if (typeof error === 'string') return error;
    if (error?.message) return error.message;
    if (error?.detail) return error.detail;
    return 'An unexpected error occurred. Please try again.';
  };

  const getErrorCode = (error) => {
    if (error?.error_code) return error.error_code;
    if (error?.code) return error.code;
    return null;
  };

  return (
    <div className="error-display">
      <div className="error-content">
        {getErrorIcon(getErrorCode(error))}
        <h3>{title}</h3>
        <p className="error-message">{getErrorMessage(error)}</p>
        
        {getErrorCode(error) && (
          <p className="error-code">Error Code: {getErrorCode(error)}</p>
        )}
        
        {showRetry && onRetry && (
          <button 
            onClick={onRetry}
            className="retry-button"
          >
            <RefreshCw size={16} />
            Try Again
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorDisplay;
