from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class BudgetTier(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class RecommendationRequest(BaseModel):
    location: str = Field(..., min_length=1, max_length=80)
    # New preferred budget inputs (numeric, in INR for two)
    budget_min: Optional[int] = Field(default=None, ge=0, le=100000)
    budget_max: Optional[int] = Field(default=None, ge=0, le=100000)
    # Legacy support (will be removed later)
    budget_tier: Optional[BudgetTier] = None
    cuisines: list[str] = Field(default_factory=list, max_length=10)
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    additional_preferences: list[str] = Field(default_factory=list, max_length=10)
    max_results: int = Field(default=5, ge=1, le=10)

    @field_validator("location")
    @classmethod
    def _validate_location(cls, value: str) -> str:
        cleaned = " ".join(value.strip().split())
        if not cleaned:
            raise ValueError("location must not be empty")
        return cleaned

    @field_validator("cuisines")
    @classmethod
    def _validate_cuisines(cls, values: list[str]) -> list[str]:
        cleaned = [" ".join(v.strip().split()) for v in values if v and v.strip()]
        deduped = list(dict.fromkeys(cleaned))
        return deduped

    @field_validator("additional_preferences")
    @classmethod
    def _validate_preferences(cls, values: list[str]) -> list[str]:
        cleaned = [" ".join(v.strip().split()) for v in values if v and v.strip()]
        deduped = list(dict.fromkeys(cleaned))
        return deduped


class NormalizedPreferences(BaseModel):
    location: str
    budget_tier: Optional[BudgetTier]
    budget_min: int
    budget_max: Optional[int]
    cuisines: list[str]
    min_rating: float
    additional_preferences: list[str]
    max_results: int


class RecommendationIntakeResponse(BaseModel):
    message: str
    normalized_preferences: NormalizedPreferences

