import os
import hashlib
import threading
import concurrent.futures
import time
import PyPDF2
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
import re

class SpeedGraph(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
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
        
        if width <= 1 or height <= 1: return
            
        for y in [0.25, 0.5, 0.75]:
            self.create_line(0, height * y, width, height * y, fill="#2A2A2A")
            
        max_val = max(max(self.data), 10) 
        points = [(0, height)]
        step = width / (self.max_points - 1)
        
        for i, val in enumerate(self.data):
            x = i * step
            y = height - (val / max_val * height * 0.85)
            points.append((x, y))
            
        points.append((width, height))
        self.create_polygon(points, fill="#1F538D", outline="")
        
        line_points = points[1:-1]
        if len(line_points) > 1:
            self.create_line(line_points, fill="#3B8ED0", width=2)
            
        self.create_text(10, 10, text=f"Current Speed: {speed_mb:.1f} MB/s", fill="white", anchor="nw", font=("Arial", 14, "bold"))

class HashingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Forensic File Hasher")
        self.root.geometry("800x700")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.root.configure(bg="#121212")
        
        self.drop_area = ctk.CTkFrame(root, height=300, fg_color=("#2A2A2A"))
        self.drop_area.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")
        self.drop_area.pack_propagate(False)
        
        # Swapped the static label for a text box to display match results
        self.result_box = ctk.CTkTextbox(self.drop_area, font=("Consolas", 14), text_color="white", fg_color="transparent")
        self.result_box.pack(expand=True, fill="both", padx=10, pady=10)
        self.result_box.insert("end", "\n\n\n\n\n\n\n\n\n\n                                  Drag and Drop files here")
        self.result_box.configure(state="disabled")
        
        self.hash_option = ctk.StringVar(value="Both")
        self.report_path = None
        
        self.radio_frame = ctk.CTkFrame(root, fg_color=("#1F1F1F"))
        self.radio_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        
        self.md5_radio = ctk.CTkRadioButton(self.radio_frame, text="MD5", variable=self.hash_option, value="MD5", text_color="white")
        self.sha256_radio = ctk.CTkRadioButton(self.radio_frame, text="SHA256", variable=self.hash_option, value="SHA256", text_color="white")
        self.both_radio = ctk.CTkRadioButton(self.radio_frame, text="Both", variable=self.hash_option, value="Both", text_color="white")
        
        self.md5_radio.pack(side="left", padx=15, pady=10)
        self.sha256_radio.pack(side="left", padx=15, pady=10)
        self.both_radio.pack(side="left", padx=15, pady=10)
        
        self.pdf_button = ctk.CTkButton(self.radio_frame, text="Load PDF Report", command=self.load_pdf)
        self.pdf_button.pack(side="right", padx=15, pady=10)
        
        self.pdf_label = ctk.CTkLabel(self.radio_frame, text="No PDF loaded", text_color="gray")
        self.pdf_label.pack(side="right", padx=5)
        
        self.start_button = ctk.CTkButton(root, text="Compute Hash", command=self.start_processing)
        self.start_button.grid(row=3, column=0, pady=10, padx=10, sticky="ew")
        
        self.status_label = ctk.CTkLabel(root, text="Status: Waiting for files...", font=("Arial", 16), text_color="white", bg_color="#121212")
        self.status_label.grid(row=3, column=1, pady=10, padx=10, sticky="ew")
        
        self.progress_bar = ctk.CTkProgressBar(root)
        self.progress_bar.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        self.progress_bar.set(0) 
        
        self.speed_graph = SpeedGraph(root, height=100)
        self.speed_graph.grid(row=5, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        
        self.files = []
        
        # Bind drop events to both the frame and the textbox inside it
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind("<<Drop>>", self.drop)
        self.result_box.drop_target_register(DND_FILES)
        self.result_box.dnd_bind("<<Drop>>", self.drop)
        
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

    def load_pdf(self):
        # Default to the directory of the first dropped file if available
        start_dir = None
        if self.files:
            start_dir = os.path.dirname(self.files[0])
            
        file_path = filedialog.askopenfilename(
            initialdir=start_dir,
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if file_path:
            self.report_path = file_path
            self.pdf_label.configure(text=os.path.basename(file_path), text_color="#00FF00")

    def extract_hashes_from_pdf(self, pdf_path):
        hashes = {"MD5": set(), "SHA256": set()}
        
        # Regex patterns for exact 32 and 64 character hex strings
        md5_pattern = re.compile(r'\b[a-fA-F0-9]{32}\b')
        sha256_pattern = re.compile(r'\b[a-fA-F0-9]{64}\b')
        
        try:
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        # Find all matches anywhere in the raw page text
                        for match in md5_pattern.findall(text):
                            hashes["MD5"].add(match.lower())
                        for match in sha256_pattern.findall(text):
                            hashes["SHA256"].add(match.lower())
        except Exception as e:
            pass
        return hashes

    def drop(self, event):
        raw_paths = self.root.tk.splitlist(event.data)
        expanded_files = []
        
        # Expand directories if the user drops a whole folder
        for path in raw_paths:
            if os.path.isdir(path):
                for root_dir, _, filenames in os.walk(path):
                    for filename in filenames:
                        expanded_files.append(os.path.join(root_dir, filename))
            else:
                expanded_files.append(path)
                
        # Auto-detect the PDF report 
        for file in expanded_files:
            if file.lower().endswith('.pdf'):
                self.report_path = file
                self.pdf_label.configure(text=os.path.basename(file), text_color="#00FF00")
                expanded_files.remove(file) # Remove the report from the hashing queue
                break # Grab the first PDF found
                
        self.files.extend(expanded_files)
        
        # Update the text box to show what will be hashed
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.insert("end", "\n".join(self.files))
        self.result_box.configure(state="disabled")
        
        self.status_label.configure(text=f"{len(self.files)} file(s) queued")
    
    def compute_hashes(self, file_path, hash_type, total_size):
        try:
            hashes = {}
            md5_hasher = hashlib.md5()
            sha256_hasher = hashlib.sha256()
            
            chunk_size = 1048576 
            bytes_since_update = 0
            
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    if hash_type in ["MD5", "Both"]:
                        md5_hasher.update(chunk)
                    if hash_type in ["SHA256", "Both"]:
                        sha256_hasher.update(chunk)
                        
                    bytes_since_update += len(chunk)
                    
                    if bytes_since_update >= 10485760:
                        with self.progress_lock:
                            self.processed_bytes += bytes_since_update
                            self.chunk_bytes_interval += bytes_since_update
                            
                            progress = self.processed_bytes / total_size
                            now = time.time()
                            elapsed_overall = now - self.start_time
                            elapsed_interval = now - self.last_interval_time
                            
                            if elapsed_interval >= 0.5:
                                instant_mb = (self.chunk_bytes_interval / elapsed_interval) / (1024 * 1024)
                                self.root.after(0, self.speed_graph.update_graph, instant_mb)
                                self.last_interval_time = now
                                self.chunk_bytes_interval = 0
                                
                            if elapsed_overall > 1.0 and self.processed_bytes > 0:
                                avg_speed = self.processed_bytes / elapsed_overall
                                eta_seconds = (total_size - self.processed_bytes) / avg_speed
                                mins, secs = divmod(int(eta_seconds), 60)
                                hrs, mins = divmod(mins, 60)
                                eta_str = f"ETA: {hrs:02d}h {mins:02d}m {secs:02d}s" if hrs > 0 else f"ETA: {mins:02d}m {secs:02d}s"
                            else:
                                eta_str = "Calculating ETA..."
                        
                        self.root.after(0, self.progress_bar.set, progress)
                        self.root.after(0, lambda t=eta_str: self.status_label.configure(text=t))
                        bytes_since_update = 0
            
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
        self.root.after(0, lambda: self.status_label.configure(text="Processing..."))
        
        total_size = sum(os.path.getsize(file) for file in self.files)
        if total_size == 0: total_size = 1  
            
        self.processed_bytes = 0
        self.chunk_bytes_interval = 0
        self.progress_lock = threading.Lock()
        
        self.start_time = time.time()  
        self.last_interval_time = self.start_time 
        
        results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_file = {executor.submit(self.compute_hashes, file, self.hash_option.get(), total_size): file for file in self.files}
            for future in concurrent.futures.as_completed(future_to_file):
                file, hashes = future.result()
                results[file] = hashes
                
        # Parse the PDF for comparison values
        pdf_hashes = self.extract_hashes_from_pdf(self.report_path) if self.report_path else None
        match_log = "--- HASH COMPARISON RESULTS ---\n"
        
        # Iterate over results, log to text file with full path, and update GUI output
        for file, hashes in results.items():
            match_log += f"\nFILE: {os.path.basename(file)}\n"
            save_path = os.path.join(os.path.dirname(file), "Hashes.txt")
            
            with open(save_path, "a") as f:
                f.write(f"{file}:\n") 
                
                for algo, hash_value in hashes.items():
                    if "Error" in algo:
                        error_line = f"  Error: {hash_value}\n"
                        f.write(error_line)
                        match_log += error_line
                        continue
                    
                    # Determine formatting based on whether a PDF report is loaded
                    if pdf_hashes:
                        is_match = hash_value.lower() in pdf_hashes.get(algo, set())
                        status = "[MATCH]" if is_match else "[NOT FOUND IN REPORT]"
                        result_line = f"  {algo}: {status} ({hash_value})\n"
                    else:
                        result_line = f"  {algo}: {hash_value}\n"
                        
                    # Write the formatted line to both the file and the GUI log
                    f.write(result_line)
                    match_log += result_line
                
                f.write("\n")
            
        # Push the match results to the GUI drop area
        def update_gui_results():
            self.result_box.configure(state="normal")
            self.result_box.delete("1.0", "end")
            self.result_box.insert("end", match_log)
            self.result_box.configure(state="disabled")
            
            elapsed_time = time.time() - self.start_time
            self.progress_bar.set(1) 
            self.status_label.configure(text=f"Complete (Time: {elapsed_time:.2f} sec)")
            self.files.clear()

        self.root.after(0, update_gui_results)

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = HashingApp(root)
    root.mainloop()