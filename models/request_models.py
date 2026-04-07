from pydantic import BaseModel
from typing import List, Literal

class BaseContentRequest(BaseModel):
    primary_keyword: str
    secondary_keywords: List[str]

    target_audience: str

    funnel_stage: Literal["Awareness", "Consideration", "Decision"]
    target_location: Literal["US", "India", "Worldwide"]

    word_count: Literal[1200, 1500, 2000]

    page_objective: Literal["Generate Leads", "Generate Traffic"]
    page_type: Literal["Blog", "Product", "Listicle", "Use Case", "Success Story"]
    brand_tone: Literal["Professional", "Conversational", "Authoritative"]

    # ✅ NEW FIELDS
    website_url: str
    key_services: List[str]
    key_competitors: List[str]


class CreateArticleRequest(BaseContentRequest):
    task_type: Literal["create"]
    topic: str


class OptimizeArticleRequest(BaseContentRequest):
    task_type: Literal["optimize"]
    page_url: str

class ApproveBriefRequest(BaseModel):
    session_id: str