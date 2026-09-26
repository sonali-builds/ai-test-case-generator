from fastapi import FastAPI, Depends

from .generator import FakeGenerator, get_generator
from .models import GenerateRequest, TestSuite

# Create the web application
app = FastAPI(title="AI Test Case Generator")

# Health check: answers "I'm alive"
@app.get("/health")
def health():
    return {"status":"ok"}


# Generate test cases for a requirement
@app.post("/generate", response_model=TestSuite)
def generate(req: GenerateRequest, gen: FakeGenerator = Depends(get_generator)):
    return gen.generate(req.requirement, req.max_cases)