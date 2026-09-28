from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException

load_dotenv() # reads OPENAI_API_KEY from the .env file, if present

from .generator import GenerationError, Generator , get_generator  # noqa: E402
from .models import GenerateRequest, TestSuite  # noqa: E402

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