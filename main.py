from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
import json
from huffman import HuffmanCoder

app = FastAPI(title="ZipMasters API")

# Serve the static HTML frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory store for the reverse mapping (Tree structure)
# Note: In a production app, you would embed this mapping into the header 
# of the compressed file itself so it's fully standalone.
tree_storage = {}

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", "r") as f:
        return f.read()

@app.post("/compress")
async def compress_file(file: UploadFile = File(...)):
    # Read text file
    content = await file.read()
    text = content.decode('utf-8')
    
    # Initialize Huffman Coder
    coder = HuffmanCoder()
    compressed_bytes, reverse_mapping = coder.compress(text)
    
    # Store tree for decompression demo
    file_id = file.filename
    tree_storage[file_id] = reverse_mapping
    
    # Return binary file
    headers = {
        'Content-Disposition': f'attachment; filename="compressed_{file.filename}.bin"'
    }
    return Response(content=compressed_bytes, headers=headers, media_type="application/octet-stream")

@app.post("/decompress")
async def decompress_file(
    file: UploadFile = File(...), 
    original_filename: str = Form(...)
):
    # Read the compressed binary file
    compressed_bytes = await file.read()
    
    # Retrieve the tree (reverse mapping) from our temporary server memory.
    # We look it up using the original text file's name.
    if original_filename not in tree_storage:
        return Response(
            content="Error: Huffman tree mapping not found. Please ensure you compressed this file in the current server session.", 
            status_code=400
        )
    
    reverse_mapping = tree_storage[original_filename]
    
    # Initialize the decoder and run the algorithm
    coder = HuffmanCoder()
    decompressed_text = coder.decompress(compressed_bytes, reverse_mapping)
    
    # Return the decoded text as a downloadable file
    headers = {
        'Content-Disposition': f'attachment; filename="restored_{original_filename}"'
    }
    return Response(content=decompressed_text, headers=headers, media_type="text/plain")

# Run this using: uvicorn main:app --reload