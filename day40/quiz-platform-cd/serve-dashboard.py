#!/usr/bin/env python3
"""
Simple HTTP server to serve the Quiz Platform CD Dashboard
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

def main():
    # Change to the project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    PORT = 3000
    
    # Check if dashboard.html exists
    if not os.path.exists('dashboard.html'):
        print("❌ Error: dashboard.html not found!")
        print("Make sure you're running this from the project directory.")
        sys.exit(1)
    
    # Create a custom handler that serves the dashboard
    class DashboardHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # Add CORS headers to allow cross-origin requests
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
        
        def do_GET(self):
            if self.path == '/' or self.path == '/dashboard':
                self.path = '/dashboard.html'
            return super().do_GET()
    
    try:
        with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
            print("🚀 Quiz Platform CD Dashboard Server")
            print("=" * 40)
            print(f"📊 Dashboard URL: http://localhost:{PORT}")
            print(f"📁 Serving from: {project_dir}")
            print("🔄 Auto-refresh: Every 30 seconds")
            print("⏹️  Press Ctrl+C to stop")
            print("=" * 40)
            
            # Try to open the dashboard in the default browser
            try:
                webbrowser.open(f'http://localhost:{PORT}')
                print("🌐 Opening dashboard in your default browser...")
            except Exception as e:
                # In WSL or headless environments, just show the URL
                print(f"🌐 Dashboard URL: http://localhost:{PORT}")
                print("   (Browser auto-open not available in this environment)")
            
            print("\n🟢 Server started successfully!")
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"❌ Error: Port {PORT} is already in use!")
            print(f"   Try a different port or stop the process using port {PORT}")
        else:
            print(f"❌ Error starting server: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
