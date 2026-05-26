from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from huffman import HuffmanCoder
from lzw import LZWCoder
import traceback

app = FastAPI(title="ZipMasters API")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/compress")
async def compress_file(file: UploadFile = File(...)):
    try:
        raw_bytes = await file.read()
        filename = (file.filename or "unknown").lower().strip()
        
        if filename.endswith('.txt'):
            coder = HuffmanCoder()
            # Returns a single, standalone byte object now!
            compressed_bytes = coder.compress(raw_bytes) 
            
        elif filename.endswith(('.docx', '.pdf', '.csv')):
            coder = LZWCoder()
            # LZW is also standalone
            compressed_bytes, _ = coder.compress(raw_bytes)
            
        else:
            # Bypass
            compressed_bytes = raw_bytes
        
        headers = {
            'Content-Disposition': f'attachment; filename="compressed_{file.filename}.bin"'
        }
        return Response(content=compressed_bytes, headers=headers, media_type="application/octet-stream")
        
    except Exception as e:
        error_trace = traceback.format_exc()
        return Response(content=f"Backend Crash during Compression:\n{error_trace}", status_code=500)


@app.post("/decompress")
async def decompress_file(
    file: UploadFile = File(...), 
    original_filename: str = Form(...)
):
    try:
        compressed_bytes = await file.read()
        target_filename = original_filename.lower().strip()
        
        # Route the decompression based purely on the target extension
        if target_filename.endswith('.txt'):
            coder = HuffmanCoder()
            # No mapping passed! The file contains its own map.
            decompressed_bytes = coder.decompress(compressed_bytes)
            
        elif target_filename.endswith(('.docx', '.pdf', '.csv')):
            coder = LZWCoder()
            decompressed_bytes = coder.decompress(compressed_bytes)
            
        else:
            decompressed_bytes = compressed_bytes
        
        headers = {
            'Content-Disposition': f'attachment; filename="restored_{original_filename}"'
        }
        return Response(content=decompressed_bytes, headers=headers, media_type="application/octet-stream")
        
    except Exception as e:
        error_trace = traceback.format_exc()
        return Response(content=f"Backend Crash during Decompression:\n{error_trace}", status_code=500)