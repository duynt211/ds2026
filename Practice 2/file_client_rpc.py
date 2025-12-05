"""
RPC File Transfer Client
Uses XML-RPC to send files to the server
"""

import xmlrpc.client
import os
import base64
import sys


def send_file(filename, host='127.0.0.1', port=8000):
    """
    Send file to RPC server
    
    Args:
        filename (str): Path to file to send
        host (str): Server host
        port (int): Server port
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Check if file exists
    if not os.path.exists(filename):
        print(f"[-] Error: File '{filename}' not found")
        return False
    
    # Get file info
    filesize = os.path.getsize(filename)
    basename = os.path.basename(filename)
    
    print("=" * 60)
    print("RPC File Transfer Client")
    print("=" * 60)
    print(f"File: {basename}")
    print(f"Size: {filesize} bytes ({filesize / 1024:.2f} KB)")
    print(f"Server: {host}:{port}")
    print("-" * 60)
    
    try:
        # Create RPC client proxy
        server_url = f"http://{host}:{port}"
        print(f"[*] Connecting to {server_url}...")
        
        proxy = xmlrpc.client.ServerProxy(server_url)
        
        # Test connection
        try:
            response = proxy.ping()
            if response == "pong":
                print("[+] Connected to server successfully")
        except Exception as e:
            print(f"[-] Cannot connect to server: {e}")
            return False
        
        # Read file and encode to base64
        print(f"[*] Reading file: {filename}")
        with open(filename, 'rb') as f:
            file_data = f.read()
        
        # Encode to base64 for transmission
        file_data_base64 = base64.b64encode(file_data).decode('utf-8')
        
        print(f"[*] Uploading file to server...")
        
        # Call RPC method to upload file
        result = proxy.upload_file(basename, file_data_base64)
        
        # Check result
        if result['status'] == 'success':
            print(f"[+] {result['message']}")
            print(f"[+] Bytes transferred: {result['size']}")
            print(f"[+] Server path: {result['path']}")
            return True
        else:
            print(f"[-] Upload failed: {result['message']}")
            return False
            
    except ConnectionRefusedError:
        print("[-] Error: Could not connect to server.")
        print("    Make sure the server is running.")
        return False
    except Exception as e:
        print(f"[-] Error: {e}")
        return False


def main():
    """Main function"""
    # Get filename from command line or user input
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = input("Enter filename to send: ").strip()
    
    # Get server details (optional)
    if len(sys.argv) > 2:
        host = sys.argv[2]
    else:
        host_input = input("Enter server IP (default 127.0.0.1): ").strip()
        host = host_input if host_input else '127.0.0.1'
    
    if len(sys.argv) > 3:
        port = int(sys.argv[3])
    else:
        port_input = input("Enter server port (default 8000): ").strip()
        port = int(port_input) if port_input else 8000
    
    # Send file
    success = send_file(filename, host, port)
    
    if success:
        print("\n" + "=" * 60)
        print("File transfer completed successfully!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("File transfer failed!")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
