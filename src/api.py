import os
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.rag import RAGOrchestrator

app = FastAPI(title="HDFC Mutual Fund FAQ API", version="1.0.0")

# Enable CORS for client-side Vercel/local hosting requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG orchestrator lazily to prevent boot timeouts on deployment
orchestrator = None

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

@app.post("/api/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    """Processes RAG queries through the compliance and security sanitizer pipeline."""
    global orchestrator
    if orchestrator is None:
        orchestrator = RAGOrchestrator()
        
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query text cannot be empty.")
    try:
        answer = orchestrator.query(request.query)
        return QueryResponse(response=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_endpoint():
    """Returns the backend service health status and the latest synchronization date."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    last_sync_path = os.path.join(base_dir, "data", "last_sync.json")
    sync_date = None
    
    if os.path.exists(last_sync_path):
        try:
            with open(last_sync_path, "r", encoding="utf-8") as f:
                sync_date = json.load(f).get("last_sync")
        except Exception:
            pass
            
    if not sync_date:
        sync_date = datetime.now().strftime("%d-%b-%Y")
        
    return {
        "status": "healthy",
        "last_sync": sync_date
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("src.api:app", host="0.0.0.0", port=port)
