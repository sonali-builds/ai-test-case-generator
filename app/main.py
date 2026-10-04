from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException

load_dotenv() # reads OPENAI_API_KEY from the .env file, if present

from .generator import GenerationError, Generator , get_generator  # noqa: E402
from .models import (DocumentIn, DocumentOut, GenerateRequest, RagGenerateRequest,
                     RagGenerateResponse, RetrievedChunk, SearchRequest, TestSuite)  # noqa: E402
from .rag import DocumentStore, get_store  #noqa: E402

# Create the web application
app = FastAPI(title="AI Test Case Generator")

# Health check: answers "I'm alive"
@app.get("/health")
def health():
    return {"status":"ok", "mode": type(get_generator()).__name__}


# Generate test cases for a requirement
@app.post("/generate", response_model=TestSuite)
def generate(req: GenerateRequest, gen: Generator = Depends(get_generator)):
    try:
        return gen.generate(req.requirement, req.max_cases)
    except GenerationError as e:
        raise HTTPException(status_code=502, detail=str(e))


# Upload a requirements document: it gets chunked & embedded
@app.post("/documents", response_model=DocumentOut, status_code=201)
def upload_document(doc: DocumentIn, store: DocumentStore = Depends(get_store)):
    try:
        doc_id, count = store.add(doc.title, doc.text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return DocumentOut(doc_id=doc_id, title=doc.title, chunk_count=count)


# Find the chunks most relevant to a query
@app.post("/documents/{doc_id}/search", response_model=list[RetrievedChunk])
def search_document(doc_id: str, req: SearchRequest, store: DocumentStore = Depends(get_store)):
    if not store.has(doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return store.search(doc_id, req.query, req.top_k)


# Generate test cases grounded in a document (RAG)
@app.post("/documents/{doc_id}/generate", response_model=RagGenerateResponse)
def generate_from_document(doc_id: str, req: RagGenerateRequest,
                           store: DocumentStore = Depends(get_store),
                           gen: Generator = Depends(get_generator)):
    if not store.has(doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
    retrieved = store.search(doc_id, req.focus, req.top_k)
    try:
        suite = gen.generate(req.focus, req.max_cases, context=retrieved)
    except GenerationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return RagGenerateResponse(test_cases=suite.test_cases, retrieved=retrieved)