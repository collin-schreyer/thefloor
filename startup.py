#!/usr/bin/env python3
import os
import sys
import webbrowser
import threading
import time
import socket
import subprocess
import platform
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent

def find_free_port():
    """Find a free port to run the server on"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def check_port_in_use(port):
    """Check if a port is already in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
            return False
    except socket.error:
        return True

def start_server(port):
    """Start the game server"""
    server_path = SCRIPT_DIR / 'game_server.py'
    
    if not server_path.exists():
        print(f"Error: game_server.py not found at {server_path}")
        sys.exit(1)
    
    # Start server as a subprocess
    try:
        cmd = [sys.executable, str(server_path)]
        env = os.environ.copy()
        # Force the server to run on the specified port
        env['PORT'] = str(port)
        
        server_process = subprocess.Popen(
            cmd,
            cwd=str(SCRIPT_DIR),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,  # Fixed: SUBPROCESS -> PIPE
            universal_newlines=True
        )
        
        return server_process
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

def wait_for_server(port, timeout=10):
    """Wait for the server to be ready"""
    start_time = time.time()
    while True:
        if time.time() - start_time > timeout:
            return False
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect(('127.0.0.1', port))
                return True
        except (socket.error, socket.timeout):
            time.sleep(0.1)

def open_browsers(port):
    """Open game and admin in separate browser windows"""
    game_url = f"http://localhost:{port}"
    admin_url = f"http://localhost:{port}/admin"
    
    print(f"Opening game at: {game_url}")
    print(f"Opening admin at: {admin_url}")
    
    # Open the game in the default browser
    webbrowser.open(game_url)
    
    # Wait a moment, then open admin in a new window
    time.sleep(0.5)
    
    # Try to open admin in a new window (works better on some systems)
    if platform.system() == 'Windows':
        webbrowser.open(admin_url, new=2)
    else:
        # For Mac/Linux, try to open in a new instance
        try:
            webbrowser.open(admin_url, new=2)
        except:
            # Fall back to default browser
            webbrowser.open(admin_url)

def main():
    """Main startup function"""
    print("Starting Face-Off Game...")
    
    # Find an available port
    port = 8000
    if check_port_in_use(port):
        port = find_free_port()
        print(f"Port 8000 is in use, using port {port} instead")
    
    # Start the server
    print(f"Starting server on port {port}...")
    server_process = start_server(port)
    
    # Wait for server to be ready
    print("Waiting for server to start...")
    if not wait_for_server(port):
        print("Server failed to start within timeout period")
        server_process.terminate()
        sys.exit(1)
    
    print("Server is ready!")
    
    # Open browsers
    open_browsers(port)
    
    print("\nFace-Off Game is now running!")
    print(f"Game: http://localhost:{port}")
    print(f"Admin: http://localhost:{port}/admin")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        # Keep the script running and show server output
        while True:
            output = server_process.stdout.readline()
            if output:
                print(output, end='')
            elif server_process.poll() is not None:
                break
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        print("Server stopped")

if __name__ == "__main__":
    main()