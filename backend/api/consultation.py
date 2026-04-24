from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from anthropic import Anthropic, APIConnectionError, APIStatusError, AsyncAnthropic
from ..db.session import get_db
from ..db.base import User, Patient, Triage, PriorityEnum
from ..schemas.patient_inquiry import SymptomInput, SpecialtyRecommendation
from .dependencies import get_current_user
from ..db.base import UserRole
from .doctors import denied_access
import json
from ..core.config import settings

router = APIRouter()
client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """Actúas como un motor de extracción de datos médicos de alta precisión para un sistema de triaje hospitalario. Tu objetivo es convertir el lenguaje natural del paciente en un objeto JSON estructurado que alimentará un modelo de Machine Learning y un sistema de direccionamiento a especialistas.

Especialidades Cubiertas: [Cardiología, Neurología, Gastroenterología, Dermatología, Ortopedia, Neumología, Ginecología, Oftalmología, Medicina General].

Instrucciones Estrictas:
1. Extracción: Identifica síntomas, duración y antecedentes mencionados.
2. Mapeo: El campo suggested_specialty debe ser exactamente uno de la lista anterior o "URGENCIAS" si detectas riesgo vital (dolor opresivo en pecho, dificultad respiratoria severa, pérdida de conciencia).
3. Vaguedad: Si el texto es incoherente, demasiado corto o no contiene síntomas claros, marca is_vague como true y sugiere Medicina General.
4. Formato: Responde EXCLUSIVAMENTE con un objeto JSON válido. No incluyas explicaciones, saludos ni prosa.

Esquema JSON Requerido:
{
  "symptoms_list": ["lista", "de", "síntomas"],
  "duration_hours": float or null,
  "severe_history": boolean,
  "suggested_specialty": "string",
  "is_vague": boolean,
  "reasoning": "Breve explicación técnica de la elección",
  "vital_signs": {
    "HR": null,
    "temperature": null,
    "spo2": null,
    "SBP": null,
    "RR": null
  }
}"""


@router.post("/recommend-specialty", 
            response_model=SpecialtyRecommendation,
            tags=['Patients'],
            summary='AI-powered patient routing and triage',
            description='Analyzes patient symptoms using LLM inference (Anthropic Claude), ' \
            'it identifies potential medical specialties, extracts clinical signs '
            'and determines urgency (If a life-threatening situation is detected, ' \
            'it triggers a high-priority triage event)'
    )
async def recommend_specialty(
    data: SymptomInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    denied_access(current_user, UserRole.PATIENT)

    patient_profile = current_user.patient_profile
    if not patient_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )

    try:
        # Call Claude
        message = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": data.description}]
    )
    except (APIConnectionError, APIStatusError) as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The assisted diagnostic service is temporarily unavailable."
    )

    # Parse response
    try:
        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        extracted = json.loads(raw.strip())
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Error parsing AI response"
        )

    # Handle vague input
    if extracted.get("is_vague"):
        return SpecialtyRecommendation(
            suggested_specialty="Medicina General",
            reasoning="Los síntomas descritos no son suficientemente específicos. Por favor, describe con más detalle tu situación.",
            is_vague=True,
            requires_urgent_attention=False,
            triage_created=False
        )

    is_urgent = extracted.get("suggested_specialty") == "URGENCIAS"
    triage_id = None

        
    # Auto-create triage if urgent
    if is_urgent:
        vital_signs = extracted.get("vital_signs", {})
        active_association = next(
            (a for a in patient_profile.doctor_associations if a.is_active), None
        )
    
        if not active_association:
            return SpecialtyRecommendation(
                suggested_specialty="URGENCIAS",
                reasoning="Your symptoms suggest a life-threatening situation. Go to the emergency room inmeadiatly or call 123. Do not wait for medical assistance.",
                #  
                is_vague=False,
                requires_urgent_attention=True,
                triage_created=False,
                triage_id=None
            )   
        new_triage = Triage(
            patient_id=patient_profile.id,
            doctor_id=active_association.doctor_id,
            description=data.description,
            symptoms=", ".join(extracted.get("symptoms_list", [])),
            HR=vital_signs.get("HR"),
            spo2=vital_signs.get("spo2"),
            temperature=vital_signs.get("temperature"),
            SBP=vital_signs.get("SBP"),
            RR=vital_signs.get("RR"),
            duration_hours=extracted.get("duration_hours"),
            severe_history=1 if extracted.get("severe_history") else 0,
            priority=PriorityEnum.ONE  # Maximum priority for urgent cases
        )
        db.add(new_triage)
        db.commit()
        db.refresh(new_triage)
        triage_id = new_triage.id

    return SpecialtyRecommendation(
        suggested_specialty=extracted.get("suggested_specialty"),
        reasoning=extracted.get("reasoning"),
        is_vague=False,
        requires_urgent_attention=is_urgent,
        triage_created=is_urgent,
        triage_id=triage_id
    )