import uuid
from fastapi import APIRouter, UploadFile, File, Query, HTTPException

from app.utils import (
    extract_text_from_txt,
    extract_text_from_pdf,
    chunk_fixed,
    chunk_by_sentence,
    get_embedding,
)
from app.core.pinecone_client import index
from app.database import init_db, save_chunk, delete_all_chunks

router = APIRouter()
init_db()  # ensures table exists on startup


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),    # Receive uploaded file from user
    strategy: str = Query(default="fixed", enum=["fixed", "sentence"]),
    chunk_size: int = Query(default=500, ge=100, le=2000),
):
    content = await file.read()  # reads the uploaded file into RAM (memory)
    filename = file.filename or "unknown"

    # 1. Extract text
    if filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(content)
    elif filename.lower().endswith(".txt"):
        text = extract_text_from_txt(content) #exttract plain text 
    else:
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported.")

    if not text.strip():
        raise HTTPException(status_code=422, detail="No text could be extracted from the file.")

    # 2. Chunk
    if strategy == "fixed":
        chunks = chunk_fixed(text, chunk_size)
    else:
        chunks = chunk_by_sentence(text)

   

    index.delete(delete_all=True)
    delete_all_chunks()
    vectors = []
    for i, chunk in enumerate(chunks): ##generates embedding, goes through each chunk 
        chunk_id = str(uuid.uuid4())
        embedding = get_embedding(chunk)  ## creates vector
        vectors.append({
            "id": chunk_id,
            "values": embedding,
            "metadata": {
                "filename": filename,
                "chunk_index": i,
                "text": chunk,
            },
        })
        save_chunk(filename, chunk_id, chunk)  #save chunk metadata to SQLite

    index.upsert(vectors=vectors)  #insert embeddings into vector DB

    return {
        "message": "File uploaded and indexed successfully.",
        "filename": filename,
        "strategy": strategy,
        "total_chunks": len(chunks),
        "chunk_preview": chunks[0][:150] if chunks else "",
    }