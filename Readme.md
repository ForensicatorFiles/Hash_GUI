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
