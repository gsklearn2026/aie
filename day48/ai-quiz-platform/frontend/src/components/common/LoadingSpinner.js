import React from 'react';
import { ClipLoader, PulseLoader } from 'react-spinners';

const LoadingSpinner = ({ 
  type = 'clip', 
  size = 35, 
  color = '#3b82f6',
  message = 'Loading...',
  fullScreen = false 
}) => {
  const spinnerComponents = {
    clip: ClipLoader,
    pulse: PulseLoader
  };
  
  const SpinnerComponent = spinnerComponents[type] || ClipLoader;
  
  const containerClass = fullScreen 
    ? 'loading-container fullscreen' 
    : 'loading-container';

  return (
    <div className={containerClass}>
      <div className="loading-content">
        <SpinnerComponent 
          color={color} 
          size={size}
          cssOverride={{
            display: "block",
            margin: "0 auto"
          }}
        />
        {message && <p className="loading-message">{message}</p>}
      </div>
    </div>
  );
};

export default LoadingSpinner;
