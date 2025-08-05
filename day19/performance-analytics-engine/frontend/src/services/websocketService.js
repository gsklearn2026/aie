class WebSocketService {
  constructor() {
    this.socket = null;
    this.callbacks = [];
  }

  connect(onMessage) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    this.socket = new WebSocket(wsUrl);
    
    this.socket.onopen = () => {
      console.log('WebSocket connected');
    };
    
    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (onMessage) {
          onMessage(data);
        }
        this.callbacks.forEach(callback => callback(data));
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
    
    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      // Attempt to reconnect after 3 seconds
      setTimeout(() => this.connect(onMessage), 3000);
    };
    
    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  addCallback(callback) {
    this.callbacks.push(callback);
  }

  removeCallback(callback) {
    this.callbacks = this.callbacks.filter(cb => cb !== callback);
  }
}

export const websocketService = new WebSocketService();
