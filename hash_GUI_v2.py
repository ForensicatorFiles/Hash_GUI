import os
import hashlib
import threading
import concurrent.futures
import time
import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk

ICON_DATA = """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"""

class SpeedGraph(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        # Initialize native CustomTkinter canvas
        super().__init__(master, bg="#121212", highlightthickness=0, **kwargs)
        self.max_points = 50
        self.data = [0] * self.max_points
        
    def reset_graph(self):
        self.data = [0] * self.max_points
        self.update_graph(0)
        
    def update_graph(self, speed_mb):
        self.data.append(speed_mb)
        if len(self.data) > self.max_points:
            self.data.pop(0)
            
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width <= 1 or height <= 1:
            return  # Canvas not fully rendered yet
            
        # Draw subtle background grid lines
        for y in [0.25, 0.5, 0.75]:
            self.create_line(0, height * y, width, height * y, fill="#2A2A2A")
            
        # Auto-scale the Y-axis based on peak speed (Minimum 10 MB/s scale)
        max_val = max(max(self.data), 10) 
        
        points = [(0, height)]
        step = width / (self.max_points - 1)
        
        for i, val in enumerate(self.data):
            x = i * step
            y = height - (val / max_val * height * 0.85) # Leave 15% padding at top
            points.append((x, y))
            
        points.append((width, height))
        
        # Draw the graph fill and accent line using CustomTkinter theme colors
        self.create_polygon(points, fill="#1F538D", outline="")
        
        line_points = points[1:-1]
        if len(line_points) > 1:
            self.create_line(line_points, fill="#3B8ED0", width=2)
            
        # Draw text overlay
        self.create_text(10, 10, text=f"Current Speed: {speed_mb:.1f} MB/s", fill="white", anchor="nw", font=("Arial", 14, "bold"))

class HashingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Hasher")
        self.root.geometry("700x650")
        
        # Load the PNG and set it as the window icon
        icon_img = tk.PhotoImage(data=ICON_DATA)
        self.root.iconphoto(False, icon_img)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.root.configure(bg="#121212")
        
        self.label = ctk.CTkLabel(root, text="Drag and drop files here", font=("Arial", 20), text_color="white", bg_color="#121212")
        self.label.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        
        self.drop_area = ctk.CTkFrame(root, height=350, width=650, fg_color=("#2A2A2A"))
        self.drop_area.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")
        
        self.drop_label = ctk.CTkLabel(self.drop_area, text="Drop files here", font=("Arial", 18), text_color="white")
        self.drop_label.pack(expand=True, pady=50)
        
        self.hash_option = ctk.StringVar(value="MD5")
        self.radio_frame = ctk.CTkFrame(root, fg_color=("#1F1F1F"))
        self.radio_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        
        self.md5_radio = ctk.CTkRadioButton(self.radio_frame, text="MD5", variable=self.hash_option, value="MD5", text_color="white")
        self.sha256_radio = ctk.CTkRadioButton(self.radio_frame, text="SHA256", variable=self.hash_option, value="SHA256", text_color="white")
        self.both_radio = ctk.CTkRadioButton(self.radio_frame, text="Both", variable=self.hash_option, value="Both", text_color="white")
        
        self.md5_radio.pack(side="left", padx=15)
        self.sha256_radio.pack(side="left", padx=15)
        self.both_radio.pack(side="left", padx=15)
        
        self.start_button = ctk.CTkButton(root, text="Compute Hash", command=self.start_processing)
        self.start_button.grid(row=3, column=0, pady=10, padx=10, sticky="ew")
        
        self.status_label = ctk.CTkLabel(root, text="Status: Waiting for files...", font=("Arial", 16), text_color="white", bg_color="#121212")
        self.status_label.grid(row=3, column=1, pady=10, padx=10, sticky="ew")

        self.progress_bar = ctk.CTkProgressBar(root)
        self.progress_bar.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        self.progress_bar.set(0) 
        
        self.speed_graph = SpeedGraph(root, height=120)
        self.speed_graph.grid(row=5, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        
        self.files = []
        
        # Ensure drag and drop works correctly
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind("<<Drop>>", self.drop)
        
        # Configure grid weights for resizing
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
    
    def drop(self, event):
        files = self.root.tk.splitlist(event.data)
        self.files.extend(files)
        self.status_label.configure(text=f"{len(self.files)} file(s) added")
    
    def compute_hashes(self, file_path, hash_type, total_size):
        try:
            hashes = {}
            md5_hasher = hashlib.md5()
            sha256_hasher = hashlib.sha256()
            
            chunk_size = 1048576  # 1MB chunks for optimal L2 Cache alignment
            bytes_since_update = 0
            
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size): 
                    if hash_type in ["MD5", "Both"]:
                        md5_hasher.update(chunk)
                    if hash_type in ["SHA256", "Both"]:
                        sha256_hasher.update(chunk)
                    
                    chunk_len = len(chunk)
                    bytes_since_update += chunk_len
                    
                    # Only lock the thread and update GUI every ~10MB 
                    # This prevents thread-locking overhead from slowing down the hashing
                    if bytes_since_update >= 10485760:
                        with self.progress_lock:
                            self.processed_bytes += bytes_since_update
                            self.chunk_bytes_interval += bytes_since_update
                            
                            progress = self.processed_bytes / total_size
                            now = time.time()
                            
                            elapsed_overall = now - self.start_time
                            elapsed_interval = now - self.last_interval_time
                            
                            # Calculate instant speed
                            if elapsed_interval >= 0.5:
                                instant_bps = self.chunk_bytes_interval / elapsed_interval
                                instant_mb = instant_bps / (1024 * 1024)
                                self.root.after(0, self.speed_graph.update_graph, instant_mb)
                                self.last_interval_time = now
                                self.chunk_bytes_interval = 0
                                
                            # Calculate ETA
                            if elapsed_overall > 1.0 and self.processed_bytes > 0:
                                avg_speed = self.processed_bytes / elapsed_overall
                                remaining_bytes = total_size - self.processed_bytes
                                eta_seconds = remaining_bytes / avg_speed
                                
                                mins, secs = divmod(int(eta_seconds), 60)
                                hrs, mins = divmod(mins, 60)
                                
                                if hrs > 0:
                                    eta_str = f"Processing... ETA: {hrs:02d}h {mins:02d}m {secs:02d}s"
                                else:
                                    eta_str = f"Processing... ETA: {mins:02d}m {secs:02d}s"
                            else:
                                eta_str = "Processing... Calculating ETA..."
                        
                        self.root.after(0, self.progress_bar.set, progress)
                        self.root.after(0, lambda t=eta_str: self.status_label.configure(text=t))
                        
                        # Reset the batch counter
                        bytes_since_update = 0
                        
            # Ensure final remaining bytes are captured and hashed 
            if hash_type in ["MD5", "Both"]:
                hashes["MD5"] = md5_hasher.hexdigest()
            if hash_type in ["SHA256", "Both"]:
                hashes["SHA256"] = sha256_hasher.hexdigest()
            
            return file_path, hashes
        except Exception as e:
            return file_path, {"Error": str(e)}
    
    def start_processing(self):
        if not self.files:
            self.status_label.configure(text="No files selected.")
            return
        
        threading.Thread(target=self.process_files, daemon=True).start()
    
    def process_files(self):
        self.root.after(0, self.progress_bar.set, 0)
        self.root.after(0, self.speed_graph.reset_graph)
        self.root.after(0, lambda: self.status_label.configure(text="Processing... Calculating ETA..."))
        
        total_size = sum(os.path.getsize(file) for file in self.files)
        if total_size == 0:
            total_size = 1  
            
        self.processed_bytes = 0
        self.chunk_bytes_interval = 0  # New tracker for instantaneous speed
        self.progress_lock = threading.Lock()
        
        self.start_time = time.time()  
        self.last_interval_time = self.start_time # Baseline for the graph
        
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_file = {executor.submit(self.compute_hashes, file, self.hash_option.get(), total_size): file for file in self.files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                file, hashes = future.result()
                results[file] = hashes
        
        for file, hashes in results.items():
            save_path = os.path.join(os.path.dirname(file), "Hashes.txt")
            with open(save_path, "a") as f:
                f.write(f"{os.path.basename(file)}:\n")
                for algo, hash_value in hashes.items():
                    f.write(f"  {algo}: {hash_value}\n")
        
        elapsed_time = time.time() - self.start_time
        self.root.after(0, self.progress_bar.set, 1) 
        self.root.after(0, lambda: self.status_label.configure(text=f"Hashes saved in Hashes.txt (Total Time: {elapsed_time:.2f} sec)"))
        self.files.clear()

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = HashingApp(root)
    root.mainloop()
