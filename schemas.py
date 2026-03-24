from pydantic import BaseModel, Field

class RefineRequest(BaseModel):
    basic_prompt: str = Field(..., min_length=3, max_length=500)

class GenerateRequest(BaseModel):
    refined_prompt: str = Field(..., min_length=10, max_length=1000)