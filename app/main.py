from fastapi import FastAPI

# Create the web application
app = FastAPI(title="AI Test Case Generator")

# Health check: answers "I'm alive"
@app.get("/health")
def health():
    return {"status":"ok"}