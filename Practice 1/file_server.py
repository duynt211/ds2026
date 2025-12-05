import socket
import os
import struct

def receive_file(conn, addr):
    """Receive file from client"""
    print(f"[+] Connection established with {addr}")
    
    try:
        # Receive filename length (4 bytes)
        filename_len_data = conn.recv(4)
        if not filename_len_data:
            print("[-] No data received")
            return
        
        filename_len = struct.unpack('!I', filename_len_data)[0]
        print(f"[*] Filename length: {filename_len}")
        
        # Receive filename
        filename = conn.recv(filename_len).decode('utf-8')
        print(f"[*] Receiving file: {filename}")
        
        # Receive file size (8 bytes)
        filesize_data = conn.recv(8)
        filesize = struct.unpack('!Q', filesize_data)[0]
        print(f"[*] File size: {filesize} bytes")
        
        # Send acknowledgment for metadata
        conn.send(b"METADATA_OK")
        
        # Create received_files directory if it doesn't exist
        os.makedirs("received_files", exist_ok=True)
        
        # Receive file data
        filepath = os.path.join("received_files", filename)
        bytes_received = 0
        
        with open(filepath, 'wb') as f:
            while bytes_received < filesize:
                # Read in chunks of 4096 bytes
                chunk_size = min(4096, filesize - bytes_received)
                data = conn.recv(chunk_size)
                
                if not data:
                    break
                
                f.write(data)
                bytes_received += len(data)
                
                # Show progress
                progress = (bytes_received / filesize) * 100
                print(f"\r[*] Progress: {progress:.2f}% ({bytes_received}/{filesize} bytes)", end='')
        
        print(f"\n[+] File received successfully: {filepath}")
        
        # Send final acknowledgment
        conn.send(b"OK")
        
    except Exception as e:
        print(f"[-] Error: {e}")
        conn.send(b"ERROR")
    
    finally:
        conn.close()

def start_server(host='0.0.0.0', port=5001):
    """Start the file transfer server"""
    # Create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Set socket options to reuse address
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind socket to address
    server_socket.bind((host, port))
    
    # Listen for connections
    server_socket.listen(5)
    print(f"[*] Server listening on {host}:{port}")
    print("[*] Waiting for connections...")
    
    try:
        while True:
            # Accept connection
            conn, addr = server_socket.accept()
            
            # Receive file (in real implementation, this should be in a separate thread)
            receive_file(conn, addr)
            
    except KeyboardInterrupt:
        print("\n[*] Server shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    print("=" * 50)
    print("TCP File Transfer Server")
    print("=" * 50)
    start_server()
