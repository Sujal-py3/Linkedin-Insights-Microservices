from typing import Annotated, Any, Callable
from pydantic import BaseModel, BeforeValidator, Field
from bson import ObjectId

# Helper to convert ObjectId to string
PyObjectId = Annotated[str, BeforeValidator(str)]

class MongoBaseModel(BaseModel):
    id: PyObjectId | None = Field(default=None, alias="_id")

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
    }
