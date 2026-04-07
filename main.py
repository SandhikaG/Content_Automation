from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from models.request_models import CreateArticleRequest, OptimizeArticleRequest
from services.claude_service import generate_content_brief, generate_full_article

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate-brief")
async def generate_brief(request: Request):
    body = await request.json()
    print(body)

    if body.get("task_type") == "create":
        parsed_request = CreateArticleRequest(**body)
    else:
        parsed_request = OptimizeArticleRequest(**body)

    return generate_content_brief(parsed_request)

@app.get("/generate-article/{session_id}")
def generate_article(session_id: str):
    return generate_full_article(session_id)