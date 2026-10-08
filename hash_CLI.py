import os
import sys
import argparse
import hashlib
import time
import threading
import concurrent.futures

class ProgressState:
    """Thread-safe object to track overall progress across multiple files."""
    def __init__(self, total_bytes):
        self.total_bytes = total_bytes
        self.processed_bytes = 0
        self.lock = threading.Lock()
        self.start_time = time.time()

def format_bytes(size):
    """Helper to convert bytes to KB, MB, GB."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def compute_hashes(file_path, hash_type, state):
    try:
        hashes = {}
        md5_hasher = hashlib.md5()
        sha256_hasher = hashlib.sha256()
        
        chunk_size = 1048576  # 1MB chunks for optimal cache alignment
        bytes_since_update = 0
        
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                if hash_type in ["md5", "both"]:
                    md5_hasher.update(chunk)
                if hash_type in ["sha256", "both"]:
                    sha256_hasher.update(chunk)
                
                chunk_len = len(chunk)
                bytes_since_update += chunk_len
                
                # Batch updates every ~10MB to prevent thread-lock overhead
                if bytes_since_update >= 10485760:
                    with state.lock:
                        state.processed_bytes += bytes_since_update
                    bytes_since_update = 0
            
            # Flush any remaining bytes to the state counter
            if bytes_since_update > 0:
                with state.lock:
                    state.processed_bytes += bytes_since_update
                    
        if hash_type in ["md5", "both"]:
            hashes["MD5"] = md5_hasher.hexdigest()
        if hash_type in ["sha256", "both"]:
            hashes["SHA256"] = sha256_hasher.hexdigest()
            
        return file_path, hashes
    except Exception as e:
        return file_path, {"Error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="High-speed CLI file hashing utility.")
    parser.add_argument("target", help="Path to a single file or a directory to hash.")
    parser.add_argument("-a", "--algorithm", choices=["md5", "sha256", "both"], default="both", 
                        help="Specify the hash algorithm: md5, sha256, or both (default: both).")
    
    args = parser.parse_args()
    target_path = os.path.abspath(args.target)
    files_to_hash = []

    if os.path.isfile(target_path):
        files_to_hash.append(target_path)
        output_dir = os.path.dirname(target_path)
    elif os.path.isdir(target_path):
        for root, _, files in os.walk(target_path):
            for file in files:
                files_to_hash.append(os.path.join(root, file))
        output_dir = target_path
    else:
        print(f"[!] Error: Target '{args.target}' does not exist.")
        return

    if not files_to_hash:
        print("[!] No files found to hash.")
        return

    # Calculate total size for the progress indicator
    total_bytes = sum(os.path.getsize(f) for f in files_to_hash)
    if total_bytes == 0: total_bytes = 1  
    
    state = ProgressState(total_bytes)
    print(f"[*] Starting {args.algorithm.upper()} hash computation for {len(files_to_hash)} file(s)...")
    print(f"[*] Total size: {format_bytes(total_bytes)}\n")
    
    results = {}
    futures = []

    # Fire off background threads
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for file in files_to_hash:
            futures.append(executor.submit(compute_hashes, file, args.algorithm, state))
        
        # Main thread loop: Update the console progress indicator
        while True:
            with state.lock:
                processed = state.processed_bytes
                
            elapsed = time.time() - state.start_time
            if elapsed > 0:
                speed_bps = processed / elapsed
            else:
                speed_bps = 0
                
            percent = (processed / total_bytes) * 100
            
            # Calculate ETA
            if speed_bps > 0:
                eta_secs = (total_bytes - processed) / speed_bps
                mins, secs = divmod(int(eta_secs), 60)
                hrs, mins = divmod(mins, 60)
                eta_str = f"{hrs:02d}h {mins:02d}m {secs:02d}s" if hrs > 0 else f"{mins:02d}m {secs:02d}s"
            else:
                eta_str = "Calculating..."
            
            # Construct the dynamic string
            status_line = f"\r[>_] Progress: {percent:05.2f}% | {format_bytes(processed)} / {format_bytes(total_bytes)} | Speed: {format_bytes(speed_bps)}/s | ETA: {eta_str}"
            
            # Print with trailing spaces to overwrite longer previous strings cleanly
            sys.stdout.write(status_line.ljust(100))
            sys.stdout.flush()
            
            # Check if all futures are done
            if all(f.done() for f in futures):
                break
                
            time.sleep(0.2)  # Update console 5 times a second
            
    # Gather results after completion
    for future in futures:
        file, hashes = future.result()
        results[file] = hashes

    # Clear the progress line and finalize
    sys.stdout.write("\r" + " " * 100 + "\r")
    sys.stdout.flush()

    output_file = os.path.join(output_dir, "Hashes.txt")
    with open(output_file, "w") as f:
        for file, hashes in results.items():
            f.write(f"{file}:\n")
            for algo, hash_value in hashes.items():
                f.write(f"  {algo}: {hash_value}\n")
            f.write("\n")

    elapsed_time = time.time() - state.start_time
    
    print("="*60)
    print(" PROCESS COMPLETE")
    print("="*60)
    print(f" Files Processed : {len(files_to_hash)}")
    print(f" Total Time      : {elapsed_time:.2f} seconds")
    print(f" Overall Speed   : {format_bytes(total_bytes / elapsed_time)}/s")
    print(f" Output Saved To : {output_file}")
    print("="*60)

if __name__ == "__main__":
    main()