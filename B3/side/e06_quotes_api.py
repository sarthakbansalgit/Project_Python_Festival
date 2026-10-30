"""Step 06, on the side: a web API in a few lines.

    uv run uvicorn e06_quotes_api:app --reload --app-dir B3/side

Then open http://127.0.0.1:8000/api/quotes and http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException

app = FastAPI(title="Quotes")

QUOTES = [
    {"id": 1, "author": "Groucho Marx", "text": "I refuse to join any club..."},
    {"id": 2, "author": "Dorothy Parker", "text": "I hate writing, I love..."},
    {"id": 3, "author": "Groucho Marx", "text": "Outside of a dog..."},
]


                                                                            
@app.get("/api/quotes")
def list_quotes(author: str | None = None) -> list[dict]:
                                                                              
    if author is None:
        return QUOTES
    result = []
    for quote in QUOTES:
        if quote["author"] == author:
            result.append(quote)
    return result


                                                                             
                                                                     
@app.get("/api/quotes/{quote_id}")
def read_quote(quote_id: int) -> dict:
    for quote in QUOTES:
        if quote["id"] == quote_id:
            return quote
    raise HTTPException(status_code=404, detail=f"No quote {quote_id}.")
