import os
import hashlib
import threading
import concurrent.futures
import time
import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD

class HashingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Hasher")
        self.root.geometry("700x500")
        
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
    
    @staticmethod
    def compute_hashes(file_path, hash_type):
        try:
            hashes = {}
            md5_hasher = hashlib.md5()
            sha256_hasher = hashlib.sha256()
            
            with open(file_path, "rb") as f:
                while chunk := f.read(10485760):  # 10MB chunks for efficiency
                    if hash_type in ["MD5", "Both"]:
                        md5_hasher.update(chunk)
                    if hash_type in ["SHA256", "Both"]:
                        sha256_hasher.update(chunk)
            
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
        self.status_label.configure(text="Processing...")
        results = {}
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_file = {executor.submit(self.compute_hashes, file, self.hash_option.get()): file for file in self.files}
            for future in concurrent.futures.as_completed(future_to_file):
                file, hashes = future.result()
                results[file] = hashes
        
        for file, hashes in results.items():
            save_path = os.path.join(os.path.dirname(file), "Hashes.txt")
            with open(save_path, "a") as f:
                f.write(f"{os.path.basename(file)}:\n")
                for algo, hash_value in hashes.items():
                    f.write(f"  {algo}: {hash_value}\n")
        
        elapsed_time = time.time() - start_time
        self.status_label.configure(text=f"Hashes saved in Hashes.txt (Time: {elapsed_time:.2f} sec)")
        self.files.clear()

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = HashingApp(root)
    root.mainloop()
