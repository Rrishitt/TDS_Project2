from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import numpy as np
import requests
import logging
import uvicorn

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.DEBUG)


# Define request model
class SearchRequest(BaseModel):
    docs: List[str]
    query: str


# Define response model
class SearchResponse(BaseModel):
    matches: List[str]


# Proxy Configuration
API_URL = "https://aiproxy.sanand.workers.dev/openai/v1/embeddings"
# Replace with your AIPROXY_TOKEN
AIPROXY_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjIwMDQ1OTVAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.7B5ZZjxXdte_XTR9x7UGkOzvekGIJjSNcJ6Zrb2NVbk"

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Get embeddings for a list of texts using the proxy API"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {AIPROXY_TOKEN}",
        }
        payload = {
            "model": "text-embedding-3-small",  # Update model if needed
            "input": texts,
        }

        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()

        # Extract embeddings
        data = response.json()
        return [item["embedding"] for item in data["data"]]

    except Exception as e:
        logging.error(f"Error fetching embeddings: {e}")
        raise


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    v1_array = np.array(v1)
    v2_array = np.array(v2)
    if not v1_array.any() or not v2_array.any():
        raise ValueError("One or both vectors are empty")
    return np.dot(v1_array, v2_array) / (
        np.linalg.norm(v1_array) * np.linalg.norm(v2_array)
    )


@app.post("/similarity")
async def get_similar_docs(request: SearchRequest) -> SearchResponse:
    try:
        logging.debug(f"Received request: {request}")

        # Get embeddings for all texts
        all_texts = request.docs + [request.query]
        embeddings = get_embeddings(all_texts)

        # Separate document embeddings and query embedding
        doc_embeddings = embeddings[:-1]
        query_embedding = embeddings[-1]

        # Calculate similarities
        similarities = [
            (i, cosine_similarity(doc_emb, query_embedding))
            for i, doc_emb in enumerate(doc_embeddings)
        ]

        # Sort by similarity score in descending order
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Get top 3 most similar documents
        top_matches = [request.docs[idx] for idx, _ in similarities[:3]]

        return SearchResponse(matches=top_matches)

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000, reload=True)
# uvicorn ga3_7:app --host 0.0.0.0 --port 10000 --reload
