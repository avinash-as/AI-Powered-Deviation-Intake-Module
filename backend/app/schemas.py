from typing import Optional
from pydantic import BaseModel, Field


class DeviationBase(BaseModel):
    title: str = ""
    description: str = ""
    date_observed: str = ""
    observed_by: str = ""
    department: str = ""
    product: str = ""
    batch_no: str = ""
    stage: str = ""
    equipment: str = ""
    specification_limit: str = ""
    observed_value: str = ""
    deviation_type: str = "Process"
    severity: str = "Minor"
    impact_assessment: str = ""
    probable_cause: str = ""
    immediate_action: str = ""
    capa_required: bool = False
    status: str = "Logged"
    ai_reason: str = ""
    ai_confidence: float = 0.0


class DeviationCreate(DeviationBase):
    pass


class DeviationOut(DeviationBase):
    id: int
    deviation_id: str

    class Config:
        from_attributes = True


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=10, description="Pasted deviation text / email body")


class ExtractedDeviation(DeviationBase):
    pass


class AnalyzeResponse(BaseModel):
    extracted: ExtractedDeviation
    severity: str
    impact_assessment: str
    ai_reason: str
    ai_confidence: float
    provider: str  # "groq" or "heuristic-fallback"
    raw_text_chars: int
