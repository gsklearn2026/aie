import toast from 'react-hot-toast';

class ErrorHandler {
  static handleError(error, context = {}) {
    console.error('Error occurred:', error, context);
    
    let userMessage = 'An unexpected error occurred';
    let shouldRetry = false;
    
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      if (data && data.message) {
        userMessage = data.message;
      }
      
      if (data && data.details && data.details.recoverable) {
        shouldRetry = true;
      }
      
      // Handle specific status codes
      switch (status) {
        case 401:
          userMessage = 'Please log in again to continue';
          // Redirect to login
          setTimeout(() => {
            window.location.href = '/login';
          }, 2000);
          break;
        case 429:
          userMessage = 'Too many requests. Please wait a moment.';
          shouldRetry = true;
          break;
        case 503:
          userMessage = 'Service temporarily unavailable. Retrying...';
          shouldRetry = true;
          break;
      }
    } else if (error.request) {
      // Network error
      userMessage = 'Network connection issue. Please check your internet.';
      shouldRetry = true;
    }
    
    // Show user-friendly toast
    toast.error(userMessage, {
      duration: shouldRetry ? 5000 : 4000,
      position: 'top-right',
    });
    
    return { userMessage, shouldRetry };
  }
  
  static async withRetry(apiCall, maxRetries = 3, delay = 1000) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await apiCall();
      } catch (error) {
        if (attempt === maxRetries) {
          throw error;
        }
        
        const { shouldRetry } = this.handleError(error, { attempt });
        
        if (!shouldRetry) {
          throw error;
        }
        
        // Exponential backoff
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, attempt - 1)));
      }
    }
  }
}

export default ErrorHandler;
