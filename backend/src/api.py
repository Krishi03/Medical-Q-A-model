from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llm_interface import LLMInterface
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()
llm_interface = LLMInterface(api_key=os.getenv('GOOGLE_API_KEY'))

class Query(BaseModel):
    text: str
    urls: list[str] = []  # Optional list of URLs to scrape

@app.post("/api/query")
async def process_query(query: Query):
    try:
        # If URLs are provided, update knowledge base first
        if query.urls:
            llm_interface.update_knowledge_base(query.urls)
        
        # Generate response using both existing and new data
        response = llm_interface.generate_response(query.text)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)