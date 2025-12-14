from typing import List, Optional
from datetime import datetime
from pydantic import Field, HttpUrl
from app.models.common import MongoBaseModel

class Post(MongoBaseModel):
    page_id: str
    post_id: str  # li:activity:urn
    content: str
    likes: int = 0
    comments_count: int = 0
    media_url: Optional[str] = None
    created_at: Optional[datetime] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)

class Employee(MongoBaseModel):
    page_id: str
    name: str
    title: Optional[str] = None
    profile_url: Optional[str] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)

class Page(MongoBaseModel):
    page_id: str = Field(..., description="The unique identifier from the URL, e.g. deepsolv")
    name: str
    linkedin_id: Optional[str] = None
    url: str
    profile_picture: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    followers: int = 0
    head_count: int = 0
    specialities: List[str] = []
    
    # We store posts/employees in separate collections for scalability, 
    # but might embed summaries or recent items here if needed.
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
