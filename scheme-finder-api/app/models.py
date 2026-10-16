"""Data models and enums for Government Scheme Finder Bot."""

from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class IndianState(str, Enum):
    ANDHRA_PRADESH = "Andhra Pradesh"
    ARUNACHAL_PRADESH = "Arunachal Pradesh"
    ASSAM = "Assam"
    BIHAR = "Bihar"
    CHHATTISGARH = "Chhattisgarh"
    GOA = "Goa"
    GUJARAT = "Gujarat"
    HARYANA = "Haryana"
    HIMACHAL_PRADESH = "Himachal Pradesh"
    JHARKHAND = "Jharkhand"
    KARNATAKA = "Karnataka"
    KERALA = "Kerala"
    MADHYA_PRADESH = "Madhya Pradesh"
    MAHARASHTRA = "Maharashtra"
    MANIPUR = "Manipur"
    MEGHALAYA = "Meghalaya"
    MIZORAM = "Mizoram"
    NAGALAND = "Nagaland"
    ODISHA = "Odisha"
    PUNJAB = "Punjab"
    RAJASTHAN = "Rajasthan"
    SIKKIM = "Sikkim"
    TAMIL_NADU = "Tamil Nadu"
    TELANGANA = "Telangana"
    TRIPURA = "Tripura"
    UTTAR_PRADESH = "Uttar Pradesh"
    UTTARAKHAND = "Uttarakhand"
    WEST_BENGAL = "West Bengal"
    ANDAMAN_AND_NICOBAR = "Andaman and Nicobar Islands"
    CHANDIGARH = "Chandigarh"
    DADRA_AND_NAGAR_HAVELI_DAMAN_DIU = "Dadra and Nagar Haveli and Daman and Diu"
    DELHI = "Delhi"
    JAMMU_AND_KASHMIR = "Jammu and Kashmir"
    LADAKH = "Ladakh"
    LAKSHADWEEP = "Lakshadweep"
    PUDUCHERRY = "Puducherry"


class SocialCategory(str, Enum):
    SC = "SC"
    ST = "ST"
    OBC = "OBC"
    GENERAL = "General"
    EWS = "EWS"
    OTHER = "Other"


class Occupation(str, Enum):
    STUDENT = "student"
    FARMER = "farmer"
    DAILY_WAGE = "daily_wage"
    SALARIED = "salaried"
    SELF_EMPLOYED = "self_employed"
    UNEMPLOYED = "unemployed"
    HOMEMAKER = "homemaker"
    RETIRED = "retired"
    OTHER = "other"


class Verdict(str, Enum):
    ELIGIBLE = "eligible"
    POSSIBLY_ELIGIBLE = "possibly_eligible"
    NOT_ELIGIBLE = "not_eligible"


class Profile(BaseModel):
    """Citizen questionnaire profile."""
    model_config = ConfigDict(extra="forbid")

    age: Optional[int] = Field(default=None, ge=0, le=120, description="Age in years (0 to 120)")
    annual_income: Optional[int] = Field(default=None, ge=0, description="Annual income in Rupees (>= 0)")
    state: Optional[IndianState] = Field(default=None, description="Indian State or Union Territory")
    category: Optional[SocialCategory] = Field(default=None, description="Social Category")
    occupation: Optional[Occupation] = Field(default=None, description="Current occupation")


class SchemeCriterion(BaseModel):
    """Single eligibility rule criterion."""
    field: str
    op: str
    value: Any


class Scheme(BaseModel):
    """Government scheme record."""
    id: str
    name: str
    name_kn: Optional[str] = None
    benefit: str
    criteria: List[SchemeCriterion] = Field(default_factory=list)
    source_url: str
    last_verified: Optional[str] = None
    status: str = "draft_unverified"


class EligibilityResult(BaseModel):
    """Evaluated verdict for a scheme."""
    scheme_id: str
    name: str
    name_kn: Optional[str] = None
    benefit: str
    source_url: str
    verdict: str  # "eligible", "possibly_eligible", or "not_eligible"
    missing_fields: List[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    """Chat message request."""
    question: str = Field(..., min_length=1, max_length=500, description="User question (1-500 chars)")
    profile: Optional[Profile] = None


class ChatResponse(BaseModel):
    """Grounded chatbot response."""
    answer: str
    language: str  # "en" or "kn"
    sources: List[str] = Field(default_factory=list)
    used_scheme_ids: List[str] = Field(default_factory=list)
