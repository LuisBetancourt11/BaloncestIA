"""Pydantic schemas for request validation and response shapes.

Keep schema changes backwards-compatible when possible; they are used by
FastAPI to validate incoming JSON payloads.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any


class PlanRequest(BaseModel):
    """Input payload for plan generation.

    - `nivel` must be one of: principiante, intermedio, avanzado
    - `disponibilidad` is a list of day codes accepted by the planner
    """
    nivel: str = Field(..., regex='^(principiante|intermedio|avanzado)$')
    semanas: Optional[int] = 4
    disponibilidad: List[str]
    duracion_sesion_min: int
    objetivos: List[str]
    equipamiento: List[str]
    preferencias: Optional[dict] = None
    historial_carga: Optional[List[dict]] = None


class PlanResponse(BaseModel):
    plan_id: int
    resumen: Any


class FeedbackIn(BaseModel):
    plan_id: int
    week_idx: int
    cumplimiento_pct: int
    rpe_promedio: int
    notas: Optional[str] = None
