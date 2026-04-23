from pydantic import BaseModel

class SymptomInput(BaseModel):
    description: str


class SpecialtyRecommendation(BaseModel):
    suggested_specialty: str
    reasoning: str
    is_vague: bool
    requires_urgent_attention: bool
    triage_created: bool
    triage_id: int | None = None
