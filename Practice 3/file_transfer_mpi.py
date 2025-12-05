"""
MPI File Transfer - Combined Sender and Receiver

This script implements an MPI-based file transfer system where:
- Rank 0 acts as the receiver (server)
- Rank 1 acts as the sender (client)

Usage:
    mpiexec -n 2 python file_transfer_mpi.py <filename>
    
Example:
    mpiexec -n 2 python file_transfer_mpi.py test_file.txt
"""

from mpi4py import MPI
import os
import sys
import numpy as np

# MPI Communicator
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Constants
CHUNK_SIZE = 4096
RECEIVER_RANK = 0
SENDER_RANK = 1


def sender_process(filename):
    """Sender process (Rank 1) - sends file to receiver"""
    print(f"[Rank {rank}] Starting sender process")
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f"[Rank {rank}] Error: File '{filename}' not found")
        return False
    
    # Get file size and basename
    filesize = os.path.getsize(filename)
    basename = os.path.basename(filename)
    
    print(f"[Rank {rank}] File: {basename}")
    print(f"[Rank {rank}] Size: {filesize} bytes")
    
    try:
        # Step 1: Send metadata (filename and size)
        metadata = {
            'filename': basename,
            'filesize': filesize
        }
        print(f"[Rank {rank}] Sending metadata to Rank {RECEIVER_RANK}...")
        comm.send(metadata, dest=RECEIVER_RANK, tag=10)
        
        # Step 2: Wait for metadata acknowledgment
        ack = comm.recv(source=RECEIVER_RANK, tag=11)
        if ack != "METADATA_OK":
            print(f"[Rank {rank}] Error: Receiver did not acknowledge metadata")
            return False
        print(f"[Rank {rank}] Metadata acknowledged")
        
        # Step 3: Send file data in chunks
        bytes_sent = 0
        with open(filename, 'rb') as f:
            while bytes_sent < filesize:
                # Read chunk
                chunk_data = f.read(CHUNK_SIZE)
                if not chunk_data:
                    break
                
                # Convert to numpy array for MPI.Send
                chunk_array = np.frombuffer(chunk_data, dtype=np.uint8)
                chunk_length = len(chunk_array)
                
                # Send chunk length first
                comm.send(chunk_length, dest=RECEIVER_RANK, tag=20)
                
                # Send chunk data
                comm.Send(chunk_array, dest=RECEIVER_RANK, tag=21)
                
                bytes_sent += chunk_length
                
                # Show progress
                progress = (bytes_sent / filesize) * 100
                print(f"\r[Rank {rank}] Progress: {progress:.2f}% ({bytes_sent}/{filesize} bytes)", end='')
        
        print(f"\n[Rank {rank}] File sent successfully")
        
        # Step 4: Send end marker
        comm.send(0, dest=RECEIVER_RANK, tag=20)
        
        # Step 5: Wait for final acknowledgment
        final_ack = comm.recv(source=RECEIVER_RANK, tag=30)
        if final_ack == "OK":
            print(f"[Rank {rank}] Transfer confirmed by receiver")
            return True
        else:
            print(f"[Rank {rank}] Warning: Receiver reported an issue")
            return False
            
    except Exception as e:
        print(f"[Rank {rank}] Error: {e}")
        return False


def receiver_process():
    """Receiver process (Rank 0) - receives file from sender"""
    print(f"[Rank {rank}] Starting receiver process")
    print(f"[Rank {rank}] Waiting for file from Rank {SENDER_RANK}...")
    
    try:
        # Step 1: Receive metadata
        metadata = comm.recv(source=SENDER_RANK, tag=10)
        filename = metadata['filename']
        filesize = metadata['filesize']
        
        print(f"[Rank {rank}] Receiving file: {filename}")
        print(f"[Rank {rank}] Expected size: {filesize} bytes")
        
        # Step 2: Send metadata acknowledgment
        comm.send("METADATA_OK", dest=SENDER_RANK, tag=11)
        
        # Step 3: Create received_files directory if needed
        os.makedirs("received_files", exist_ok=True)
        filepath = os.path.join("received_files", filename)
        
        # Step 4: Receive file data
        bytes_received = 0
        with open(filepath, 'wb') as f:
            while bytes_received < filesize:
                # Receive chunk length
                chunk_length = comm.recv(source=SENDER_RANK, tag=20)
                
                # Check for end marker
                if chunk_length == 0:
                    break
                
                # Receive chunk data
                chunk_array = np.empty(chunk_length, dtype=np.uint8)
                comm.Recv(chunk_array, source=SENDER_RANK, tag=21)
                
                # Write to file
                f.write(chunk_array.tobytes())
                bytes_received += chunk_length
                
                # Show progress
                progress = (bytes_received / filesize) * 100
                print(f"\r[Rank {rank}] Progress: {progress:.2f}% ({bytes_received}/{filesize} bytes)", end='')
        
        print(f"\n[Rank {rank}] File received successfully: {filepath}")
        
        # Step 5: Verify file size
        actual_size = os.path.getsize(filepath)
        if actual_size == filesize:
            print(f"[Rank {rank}] File integrity verified (size matches)")
            comm.send("OK", dest=SENDER_RANK, tag=30)
            return True
        else:
            print(f"[Rank {rank}] Warning: File size mismatch! Expected {filesize}, got {actual_size}")
            comm.send("SIZE_MISMATCH", dest=SENDER_RANK, tag=30)
            return False
            
    except Exception as e:
        print(f"[Rank {rank}] Error: {e}")
        comm.send("ERROR", dest=SENDER_RANK, tag=30)
        return False


def main():
    """Main function"""
    print("=" * 50)
    print(f"MPI File Transfer - Rank {rank} of {size}")
    print("=" * 50)
    
    # Check if we have exactly 2 processes
    if size != 2:
        if rank == 0:
            print(f"[Rank {rank}] Error: This program requires exactly 2 MPI processes")
            print(f"[Rank {rank}] Usage: mpiexec -n 2 python file_transfer_mpi.py <filename>")
        return
    
    if rank == SENDER_RANK:
        # Sender process
        if len(sys.argv) < 2:
            print(f"[Rank {rank}] Error: No filename provided")
            print(f"[Rank {rank}] Usage: mpiexec -n 2 python file_transfer_mpi.py <filename>")
            return
        
        filename = sys.argv[1]
        sender_process(filename)
        
    elif rank == RECEIVER_RANK:
        # Receiver process
        receiver_process()
    
    print(f"\n[Rank {rank}] Process complete")


if __name__ == "__main__":
    main()
