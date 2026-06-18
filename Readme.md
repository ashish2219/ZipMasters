# 🗜️ ZipMasters: Adaptive Compression Engine

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![Architecture](https://img.shields.io/badge/Architecture-Stateless-success.svg)
![Deployment](https://img.shields.io/badge/Deployed-Render-informational.svg)

**ZipMasters** is a high-performance, web-based file compression engine designed to solve the computational inefficiency of applying a single compression algorithm to diverse data types. Built entirely from scratch without external compression libraries, it utilizes an intelligent **Smart Router** to dynamically apply the most mathematically optimal compression strategy based on file entropy and MIME types.

---

## ✨ Key Features

- **Intelligent Algorithmic Routing:** Automatically routes low-entropy text to a Huffman Coding pipeline, structured documents (`.pdf`, `.docx`) to a Lempel-Ziv-Welch (LZW) pipeline, and bypasses high-entropy files (e.g., already compressed formats) to prevent data inflation.
- **100% Stateless Architecture:** The server retains zero memory of processed files, allowing for infinite scalability and reliable decompression after server restarts.
  - _Huffman Engine:_ Serializes its reverse-mapping prefix tree into a custom JSON-encoded binary header injected directly into the compressed `.bin` file.
  - _LZW Engine:_ Mathematically reconstructs its extended dictionary on the fly during decompression using dynamic pattern inference.
- **RESTful API Backend:** Powered by FastAPI for asynchronous, strictly in-memory binary processing, ensuring zero I/O disk latency during execution.
- **Premium User Interface:** A responsive, glassmorphic frontend featuring custom file dropzones, deterministic simulated progress tracking, and dynamic Light/Dark mode toggling.

---

## 🧠 Core Algorithms & Complexities

This project demonstrates pure implementations of fundamental Design and Analysis of Algorithms (DAA) concepts.

### 1. Huffman Coding (Greedy Approach)

Applied to raw text (`.txt`) where character frequencies vary significantly.

- **Time Complexity:** $\mathcal{O}(N \log N)$ where $N$ is the number of unique characters, driven by the Min-Heap construction.
- **Space Complexity:** $\mathcal{O}(U)$ where $U$ is the number of unique symbols stored in the prefix tree.

### 2. Lempel-Ziv-Welch / LZW (Dictionary Approach)

Applied to structured files containing repeating byte sequences.

- **Time Complexity:** $\mathcal{O}(N)$ linear time, processing the input stream in a single sequential pass.
- **Space Complexity:** $\mathcal{O}(D)$ where $D$ is the dynamically growing dictionary. In this implementation, the dictionary is securely capped at 65,536 entries (16-bit integer packing) to prevent memory exhaustion on massive files.

---

## 🚀 Installation & Local Setup

### Prerequisites

- Python 3.8 or higher installed on your system.

### Steps

1. **Clone the repository:**

   ```bash
   git clone [https://github.com/yourusername/zipmasters.git](https://github.com/yourusername/zipmasters.git)
   cd zipmasters
   ```

2. **Create a virtual environment (Recommended):**

   ```bash
   python -m venv venv
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install the required dependencies:**

   ```bash
   pip install fastapi uvicorn python-multipart
   ```

4. **Run the application:**

   ```bash
   uvicorn main:app --reload
   ```

5. **Access the application:**
   Open your browser and navigate to `http://localhost:8000`

---

## 📂 Project Structure

```text
zipmasters/
│
├── main.py              # FastAPI server, Smart Router, and API Endpoints
├── huffman.py           # Pure Python implementation of Huffman Coding (Min-Heap, Custom Headers)
├── lzw.py               # Pure Python implementation of LZW (16-bit struct packing)
│
└── static/
    └── index.html       # HTML5, CSS3, and Vanilla JS UI (Theme logic, API fetching, Progress UI)
```

---

## 📡 API Reference

### `POST /compress`

- **Description:** Accepts a raw file upload, analyzes its extension, and returns a stand-alone compressed `.bin` artifact.
- **Payload:** `multipart/form-data` containing the `file`.
- **Response:** `application/octet-stream` (Binary File Download).

### `POST /decompress`

- **Description:** Accepts a compressed `.bin` archive and the target filename, dynamically selecting the correct algorithmic decoder to restore the file flawlessly.
- **Payload:** `multipart/form-data` containing the `file` (.bin) and a string field `original_filename`.
- **Response:** `application/octet-stream` (Restored Original File Download).

---

## 🛠️ Built With

- **Backend:** Python, FastAPI, Uvicorn
- **Frontend:** HTML5, CSS3, Vanilla JavaScript, Google Fonts (Inter)
- **Standard Libraries Used:** `heapq`, `struct`, `json`, `traceback` (No external compression libraries used to preserve academic integrity).
- **Deployment Platform:** Render

---
