# Forensic File Hasher

A high-speed, thread-optimized forensic hashing utility built for maximum throughput. Designed specifically to handle massive evidentiary files (50+ GB) and raw memory dumps, this tool bypasses typical Python bottlenecks by utilizing 1MB chunking for CPU L2 cache alignment, achieving simultaneous MD5 and SHA-256 hashing speeds exceeding 500 MB/s on modern NVMe drives.

*A Forensicator Files open-source tool.*

---

## 📦 Versions Included

This repository contains three distinct versions of the tool, tailored for different investigative workflows and environments.

### 1. CLI Version (`hash_CLI.py`) - *Fastest Performance*
Built for absolute speed, headless environments, and automated processing. Strips away all GUI thread-locking overhead.
* **Folder Handling:** Drop a single file or a root directory; the script automatically recurses through all subfolders.
* **Live Telemetry:** Features a clean, in-place updating terminal progress bar showing percentage, real-time speed (MB/s), and an ETA, without flooding the console buffer.

### 2. GUI v2 (`hash_GUI_v2.py`) - *Speed-Optimized Interface*
A dark-themed desktop application built with `customtkinter`.
* **Drag-and-Drop:** Seamlessly drag files directly into the window to build your queue.
* **Scrolling Speed Graph:** Includes a custom-built, real-time canvas graph to monitor instant read speeds, making it easy to identify storage or network bottlenecks.
* **Thread-Pooling:** Processes multiple files concurrently across available CPU cores while maintaining a responsive UI.

### 3. GUI v3 (`hash_GUI_v3.py`) - *Automated PDF Verification*
Includes all the speed and UI features of v2, with the addition of automated evidence verification against extraction reports.
* **Report Ingestion:** Load a forensic PDF report (e.g., Cellebrite, Magnet) directly into the tool.
* **Regex Carving:** Aggressively scans the PDF for 32-character (MD5) and 64-character (SHA-256) hex strings, bypassing broken tables, spaces, or formatting issues.
* **Match Validation:** Automatically compares the computed file hashes against the carved report hashes, appending a `[MATCH]` or `[NOT FOUND IN REPORT]` status to both the GUI output box and the final `Hashes.txt` log.

---

## 🚀 Installation & Setup

**Prerequisites:**
Ensure you have Python 3.10+ installed. 

**Install required dependencies:**
```bash
pip install customtkinter tkinterdnd2 PyPDF2
```

*(Note: The CLI version only requires standard Python libraries and has zero external dependencies).*

---

## 💻 Usage Instructions

### Using the CLI Version
Open your terminal or command prompt and pass the target file or folder as an argument.

**Hash a single file (Both MD5 and SHA256):**
```bash
python hash_CLI.py "C:\Evidence\Raw_Dump.bin"
```

**Hash an entire directory (MD5 only):**
```bash
python hash_CLI.py "C:\Evidence\Extraction_Folder" -a md5
```

**Arguments:**
* `target`: Path to a single file or directory.
* `-a`, `--algorithm`: Specify `md5`, `sha256`, or `both` (Default is `both`).

### Using the GUI Versions (v2 & v3)
Simply run the script to launch the interface:
```bash
python hash_GUI_v3.py
```
1. Select your hashing algorithm (MD5, SHA256, or Both).
2. *(v3 Only)* Click **Load PDF Report** and select your forensic report. If you drop a folder containing a PDF, the tool will automatically detect it and set it as the active report.
3. Drag and drop your evidentiary files or folders into the UI box.
4. Click **Compute Hash**. 
5. Results are logged to a `Hashes.txt` file located in the same directory as the processed files, complete with full absolute file paths.

---

## 🛠️ Building a Standalone Executable (Optional)

If you want to compile the GUI into a single `.exe` file that can be run on analysis machines without Python installed:

1. Install PyInstaller: `pip install pyinstaller`
2. Run the build command:
```bash
pyinstaller --noconsole --onefile --collect-all customtkinter --collect-all tkinterdnd2 hash_GUI_v3.py
```
The compiled executable will be located in the `dist/` folder.
