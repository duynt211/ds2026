import socket
import os
import struct
import sys

def send_file(filename, host='127.0.0.1', port=5001):
    """Send file to server"""
    # Check if file exists
    if not os.path.exists(filename):
        print(f"[-] Error: File '{filename}' not found")
        return False
    
    # Get file size
    filesize = os.path.getsize(filename)
    print(f"[*] File: {filename}")
    print(f"[*] Size: {filesize} bytes")
    
    try:
        # Create socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connect to server
        print(f"[*] Connecting to {host}:{port}...")
        client_socket.connect((host, port))
        print("[+] Connected to server")
        
        # Get basename of file
        basename = os.path.basename(filename)
        
        # Send filename length (4 bytes)
        filename_bytes = basename.encode('utf-8')
        filename_len = len(filename_bytes)
        client_socket.send(struct.pack('!I', filename_len))
        
        # Send filename
        client_socket.send(filename_bytes)
        
        # Send file size (8 bytes)
        client_socket.send(struct.pack('!Q', filesize))
        
        # Wait for metadata acknowledgment
        metadata_ack = client_socket.recv(1024)
        if metadata_ack != b"METADATA_OK":
            print("[-] Server did not acknowledge metadata")
            return False
        
        print("[+] Metadata acknowledged by server")
        
        # Send file data
        bytes_sent = 0
        with open(filename, 'rb') as f:
            while bytes_sent < filesize:
                # Read chunk
                chunk = f.read(4096)
                if not chunk:
                    break
                
                # Send chunk
                client_socket.send(chunk)
                bytes_sent += len(chunk)
                
                # Show progress
                progress = (bytes_sent / filesize) * 100
                print(f"\r[*] Progress: {progress:.2f}% ({bytes_sent}/{filesize} bytes)", end='')
        
        print("\n[*] Waiting for server acknowledgment...")
        
        # Wait for final acknowledgment
        final_ack = client_socket.recv(1024)
        if final_ack == b"OK":
            print("[+] File sent successfully!")
            return True
        else:
            print("[-] Server reported an error")
            return False
            
    except ConnectionRefusedError:
        print("[-] Error: Could not connect to server. Make sure the server is running.")
        return False
    except Exception as e:
        print(f"[-] Error: {e}")
        return False
    finally:
        client_socket.close()

def main():
    """Main function"""
    print("=" * 50)
    print("TCP File Transfer Client")
    print("=" * 50)
    
    # Get filename from command line or user input
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = input("Enter filename to send: ")
    
    # Get server details (optional)
    host = input("Enter server IP (default 127.0.0.1): ").strip() or '127.0.0.1'
    port_input = input("Enter server port (default 5001): ").strip()
    port = int(port_input) if port_input else 5001
    
    # Send file
    send_file(filename, host, port)

if __name__ == "__main__":
    main()
