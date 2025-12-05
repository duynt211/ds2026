"""
RPC File Transfer Server
Uses XML-RPC to receive files from clients
"""

from xmlrpc.server import SimpleXMLRPCServer
import os
import base64
from datetime import datetime


class FileTransferServer:
    """RPC Server for file transfer operations"""
    
    def __init__(self):
        self.received_dir = "received_files"
        # Create received_files directory if it doesn't exist
        os.makedirs(self.received_dir, exist_ok=True)
        
    def upload_file(self, filename, file_data_base64):
        """
        RPC method to receive and save a file
        
        Args:
            filename (str): Name of the file
            file_data_base64 (str): Base64 encoded file content
            
        Returns:
            dict: Status and message
        """
        try:
            # Decode base64 data
            file_data = base64.b64decode(file_data_base64)
            
            # Create filepath
            filepath = os.path.join(self.received_dir, filename)
            
            # Write file
            with open(filepath, 'wb') as f:
                f.write(file_data)
            
            filesize = len(file_data)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"[{timestamp}] Received file: {filename} ({filesize} bytes)")
            
            return {
                'status': 'success',
                'message': f'File {filename} uploaded successfully',
                'size': filesize,
                'path': filepath
            }
            
        except Exception as e:
            error_msg = f'Error uploading file: {str(e)}'
            print(f"[-] {error_msg}")
            return {
                'status': 'error',
                'message': error_msg
            }
    
    def ping(self):
        """Simple ping method to check server availability"""
        return "pong"
    
    def get_server_info(self):
        """Get server information"""
        return {
            'name': 'RPC File Transfer Server',
            'version': '1.0',
            'received_directory': self.received_dir
        }


def start_server(host='0.0.0.0', port=8000):
    """Start the RPC server"""
    
    # Create server instance
    server = SimpleXMLRPCServer((host, port), allow_none=True)
    server.register_introspection_functions()
    
    # Create and register file transfer service
    file_service = FileTransferServer()
    server.register_instance(file_service)
    
    print("=" * 60)
    print("RPC File Transfer Server")
    print("=" * 60)
    print(f"Server listening on {host}:{port}")
    print(f"Received files will be saved to: {file_service.received_dir}/")
    print("Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server shutting down...")


if __name__ == "__main__":
    start_server()
